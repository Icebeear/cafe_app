import json
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish
from src.dish import crud
from src.dish.crud import get_dish_by_id, get_dish_by_title
from src.dish.schemas import DishRead
from src.redis.utils import redis

r = redis.get_redis_client()


async def dish_by_id(
    dish_id: Annotated[UUID4, Path],
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
            status_code=status.HTTP_404_NOT_FOUND, detail='dish not found'
        )

    if request.method == 'GET':
        r.setex(
            f'{dish.submenu_id}_dish_{dish.id}', 600, json.dumps(jsonable_encoder(dish))
        )

    dish.price = await get_new_dish_price(dish)

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


def clear_dish_cache(submenu_id: str, dish_id: str) -> None:
    redis.clear_main_cache()

    menu_key = r.keys(f'*_submenu_{submenu_id}')

    menu_id = menu_key[0].split('_')[0] if menu_key else None

    redis.clear_cache(
        f'{submenu_id}_dish_{dish_id}',
        f'{submenu_id}_dish_{dish_id}',
        f'{menu_id}_submenu_{submenu_id}',
    )


async def load_all_dishes(session: AsyncSession, offset: int, limit: int) -> list[Dish]:
    cache = r.get('all_dishes')
    params = r.get('dishes_params')

    if cache and params == f'{offset}_{limit}':
        return json.loads(cache)

    dishes = await crud.get_dishes(session, offset, limit)

    for dish in dishes:
        dish.price = await get_new_dish_price(dish)

    r.setex('all_dishes', 3600, json.dumps(jsonable_encoder(dishes)))
    r.setex('dishes_params', 3600, f'{offset}_{limit}')

    return dishes


async def get_new_dish_price(dish: Dish) -> str:
    discounts = r.get('discounts')
    dish_id = str(dish.id)

    if discounts:
        discounts = json.loads(discounts)
        if dish_id in discounts:
            discount = discounts[dish_id]

            return str(float(dish.price) - float(dish.price) * (discount / 100))

    return dish.price
