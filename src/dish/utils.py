import json
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish
from src.dish.crud import get_dish_by_id, get_dish_by_title
from src.dish.schemas import DishRead
from src.redis.utils import get_redis_client

r = get_redis_client()


async def dish_by_id(
    dish_id: Annotated[str, Path],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Dish:

    cache = r.get(f'dish_{dish_id}')

    if cache and request.method == 'GET':
        return DishRead(**json.loads(cache))

    dish = await get_dish_by_id(session, dish_id)
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )

    if request.method == 'GET':
        r.setex(f'dish_{dish.id}', 600, json.dumps(jsonable_encoder(dish)))

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


async def clear_dish_cache(dish_id: str) -> None:
    r.delete(f'dish_{dish_id}')
    r.delete('all_dishes')
