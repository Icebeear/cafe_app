import json

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish, Menu, SubMenu
from src.dish import crud
from src.dish.schemas import DishCreate, DishRead, DishUpdatePartial
from src.dish.utils import check_unique_dish, clear_dish_cache, dish_by_id
from src.menu.utils import clear_menu_cache, menu_by_id
from src.redis.utils import get_redis_client
from src.submenu.utils import clear_submenu_cache, submenu_by_id

r = get_redis_client()

router = APIRouter(
    tags=['Dish'], prefix='/menus/{menu_id}/submenus/{submenu_id}/dishes'
)


@router.post(
    '/',
    response_model=DishRead,
    status_code=status.HTTP_201_CREATED
)
async def create_dish(
    dish: DishCreate,
    menu: Menu = Depends(menu_by_id),
    submenu: SubMenu = Depends(submenu_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    """
    \f
    :param dish:
    :param menu_id:
    :param submenu_id:
    :param session:
    :return: new_dish
    """
    await check_unique_dish(session, dish.title)

    r.delete('all_dishes')
    await clear_menu_cache(menu.id)
    await clear_submenu_cache(menu.id, submenu.id)

    new_dish = await crud.create_dish(session, dish, submenu)

    return new_dish


@router.get(
    '/',
    response_model=list[DishRead],
    status_code=status.HTTP_200_OK
)
async def get_dishes(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 100,
):
    """
    \f
    :param session:
    :param offset:
    :param limit:
    :return: dishes
    """
    cache = r.get('all_dishes')

    if cache:
        return json.loads(cache)

    dishes = await crud.get_dishes(session, offset, limit)

    r.setex('all_dishes', 3600, json.dumps(jsonable_encoder(dishes)))

    return dishes


@router.get(
    '/{dish_id}',
    response_model=DishRead,
    status_code=status.HTTP_200_OK
)
async def get_dish(
    session: AsyncSession = Depends(get_async_session),
    dish: Dish = Depends(dish_by_id),
):
    """
    \f
    :param menu_id:
    :param submenu_id:
    :param dish_id:
    :param session:
    :return: dish
    """
    return dish


@router.patch(
    '/{dish_id}',
    response_model=DishRead,
    status_code=status.HTTP_200_OK
)
async def update_dish(
    dish_update: DishUpdatePartial,
    dish: Dish = Depends(dish_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    """
    \f
    :param menu_id:
    :param submenu_id:
    :param dish_update:
    :param dish_id:
    :param session:
    :return: dish
    """

    r.delete(f'{dish.submenu_id}_dish_{dish.id}')
    r.delete('all_dishes')

    return await crud.update_dish_partial(
        session=session, dish=dish, dish_update=dish_update
    )


@router.delete('/{dish_id}', status_code=status.HTTP_200_OK)
async def delete_dish(
    dish: Dish = Depends(dish_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    """
    \f
    :param menu_id:
    :param submenu_id:
    :param dish_id:
    :param session:
    :return: result
    """

    await clear_dish_cache(dish.submenu_id, dish.id)

    return await crud.delete_dish(session, dish)
