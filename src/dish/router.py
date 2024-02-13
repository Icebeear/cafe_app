from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.core.database import get_async_session
from src.core.models import Dish, Menu, SubMenu
from src.core.schemas import ErrorResponse, SuccessResponse
from src.core.services import create_background_task
from src.dish import crud
from src.dish.schemas import DishCreate, DishRead, DishUpdatePartial
from src.dish.services import (
    check_unique_dish,
    clear_dish_cache,
    dish_by_id,
    load_all_dishes,
)
from src.menu.services import clear_menu_cache, menu_by_id
from src.redis.utils import redis
from src.submenu.services import clear_submenu_cache, submenu_by_id

router = APIRouter(
    tags=['Dish'], prefix='/menus/{menu_id}/submenus/{submenu_id}/dishes'
)


@router.post(
    '/',
    response_model=DishRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать блюдо',
    responses={
        409: {
            'description': 'dish cannot be in 2 submenus at the same time',
            'model': ErrorResponse
        }
    }
)
async def create_dish(
    dish: DishCreate,
    background_tasks: BackgroundTasks,
    menu: Menu = Depends(menu_by_id),
    submenu: SubMenu = Depends(submenu_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> DishRead:
    """
    \f
    :param dish:
    :param menu_id:
    :param submenu_id:
    :param session:
    :return: new_dish
    """
    await check_unique_dish(session, dish.title)

    await create_background_task(background_tasks, redis.clear_cache, 'all_dishes')
    await create_background_task(background_tasks, clear_menu_cache, menu.id)
    await create_background_task(background_tasks, clear_submenu_cache, menu.id, submenu.id)

    new_dish = await crud.create_dish(session, dish, submenu)

    return new_dish


@router.get(
    '/',
    response_model=list[DishRead],
    status_code=status.HTTP_200_OK,
    summary='Получить все блюда'
)
async def get_dishes(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 100,
) -> list[DishRead]:
    """
    \f
    :param session:
    :param offset:
    :param limit:
    :return: dishes
    """
    dishes = await load_all_dishes(session, offset, limit)

    return dishes


@router.get(
    '/{dish_id}',
    response_model=DishRead,
    status_code=status.HTTP_200_OK,
    summary='Получить блюдо',
    responses={
        404: {
            'description': 'dish not found',
            'model': ErrorResponse
        }
    }
)
async def get_dish(
    session: AsyncSession = Depends(get_async_session),
    dish: Dish = Depends(dish_by_id),
) -> DishRead:
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
    status_code=status.HTTP_200_OK,
    summary='Обновить блюдо',
    responses={
        404: {
            'description': 'dish not found',
            'model': ErrorResponse
        }
    }
)
async def update_dish(
    dish_update: DishUpdatePartial,
    background_tasks: BackgroundTasks,
    dish: Dish = Depends(dish_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> DishRead:
    """
    \f
    :param menu_id:
    :param submenu_id:
    :param dish_update:
    :param dish_id:
    :param session:
    :return: dish
    """
    await create_background_task(
        background_tasks,
        redis.clear_cache,
        f'{dish.submenu_id}_dish_{dish.id}',
        'all_dishes',
        'all_menus_nested'
    )

    return await crud.update_dish_partial(
        session=session, dish=dish, dish_update=dish_update
    )


@router.delete(
    '/{dish_id}',
    status_code=status.HTTP_200_OK,
    summary='Удалить блюдо',
    responses={
        404: {
            'description': 'dish not found',
            'model': ErrorResponse
        },
        200: {
            'model': SuccessResponse
        }
    }
)
async def delete_dish(
    background_tasks: BackgroundTasks,
    dish: Dish = Depends(dish_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    \f
    :param menu_id:
    :param submenu_id:
    :param dish_id:
    :param session:
    :return: result
    """
    await create_background_task(background_tasks, clear_dish_cache, dish.submenu_id, dish.id)

    return await crud.delete_dish(session, dish)
