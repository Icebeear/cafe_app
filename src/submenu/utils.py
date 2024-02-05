import json
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish, SubMenu
from src.redis.utils import clear_main_cache, get_redis_client
from src.submenu.crud import get_submenu_by_id, get_submenu_by_title
from src.submenu.schemas import SubMenuRead

r = get_redis_client()


async def submenu_by_id(
    submenu_id: Annotated[str, Path],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> SubMenu:

    submenu_key = r.keys(f'*_submenu_{submenu_id}')

    cache = r.get(submenu_key[0]) if submenu_key else None

    if cache and request.method == 'GET':
        return SubMenuRead(**json.loads(cache))

    submenu = await get_submenu_by_id(session, submenu_id)
    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='submenu not found'
        )

    submenu.dishes_count = await count_dishes(session, submenu_id)

    if request.method == 'GET':
        r.setex(f'{submenu.menu_id}_submenu_{submenu.id}', 600, json.dumps(jsonable_encoder(submenu)))

    return submenu


async def check_unique_submenu(
    submenu_title: Annotated[str, Path],
    session: AsyncSession,
) -> None:
    result = await get_submenu_by_title(session, submenu_title)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='submenu cannot be in 2 menus at the same time',
        )


async def count_dishes(
    session: AsyncSession,
    submenu_id: str,
) -> int:
    query = select(Dish).where(Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    return len(result.scalars().all())


async def clear_submenu_cache(menu_id: str, submenu_id: str) -> None:
    await clear_main_cache(r)

    r.delete(f'menu_{menu_id}')
    r.delete(f'{menu_id}_submenu_{submenu_id}')

    dish_keys = r.keys(f'{submenu_id}_dish_*')

    for key in dish_keys:
        r.delete(key)
