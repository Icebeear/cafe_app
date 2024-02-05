import json
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish
from src.dish.crud import get_dish_by_id, get_dish_by_title
from src.dish.schemas import DishRead
from src.redis.utils import clear_main_cache, get_redis_client

r = get_redis_client()


async def dish_by_id(
    dish_id: Annotated[str, Path],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Dish:

    dish_key = r.keys(f'*_dish_{dish_id}')

    cache = r.get(dish_key[0]) if dish_key else None

    if cache and request.method == 'GET':
        return DishRead(**json.loads(cache))

    dish = await get_dish_by_id(session, dish_id)

    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )

    if request.method == 'GET':
        r.setex(f'{dish.submenu_id}_dish_{dish.id}', 600, json.dumps(jsonable_encoder(dish)))

    return dish


async def check_unique_dish(
    session: AsyncSession,
    dish_title: Annotated[str, Path],
) -> None:

    result = await get_dish_by_title(session, dish_title)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='dish cannot be in 2 submenus at the same time',
        )


async def clear_dish_cache(submenu_id: str, dish_id: str) -> None:
    await clear_main_cache(r)

    menu_key = r.keys(f'*_submenu_{submenu_id}')

    menu_id = menu_key[0].split('_')[0] if menu_key else None

    r.delete(f'{submenu_id}_dish_{dish_id}')
    r.delete(f'menu_{menu_id}')
    r.delete(f'{menu_id}_submenu_{submenu_id}')
