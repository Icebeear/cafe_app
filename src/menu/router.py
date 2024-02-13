from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.core.database import get_async_session
from src.core.models import Menu
from src.core.schemas import ErrorResponse, SuccessResponse
from src.core.services import create_background_task
from src.menu import crud
from src.menu.schemas import MenuCreate, MenuRead, MenuReadNested, MenuUpdatePartial
from src.menu.services import (
    check_unique_menu,
    clear_menu_cache,
    load_all_menus,
    load_all_menus_nested,
    menu_by_id,
)
from src.redis.utils import redis

router = APIRouter(tags=['Menu'], prefix='/menus')


@router.post(
    '/',
    response_model=MenuRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать меню',
)
async def create_menu(
    menu: MenuCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
) -> MenuRead:
    """
    \f
    :param menu:
    :param session:
    :return: new_menu
    """
    await check_unique_menu(menu.title, session)

    await create_background_task(background_tasks, redis.clear_cache, 'all_menus', 'all_menus_nested')

    new_menu = await crud.create_menu(session, menu)

    return new_menu


@router.get(
    '/',
    response_model=list[MenuRead],
    status_code=status.HTTP_200_OK,
    summary='Получить все меню',
)
async def get_menus(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 100,
) -> list[MenuRead]:
    """
    \f
    :param session:
    :param offset:
    :param limit:
    :return: menus
    """

    menus = await load_all_menus(session, offset, limit)

    return menus


@router.get(
    '/nested',
    response_model=list[MenuReadNested],
    status_code=status.HTTP_200_OK,
    summary='Получить все меню со всеми подменю и блюдами',
)
async def get_menus_nested(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 100,
) -> list[MenuReadNested]:
    """
    \f
    :param session:
    :param offset:
    :param limit:
    :return: menus
    """

    menus_nested = await load_all_menus_nested(session, offset, limit)

    return menus_nested


@router.get(
    '/{menu_id}', response_model=MenuRead,
    status_code=status.HTTP_200_OK,
    summary='Получить меню',
    responses={
        404: {
            'description': 'menu not found',
            'model': ErrorResponse
        }
    }
)
async def get_menu(menu: Menu = Depends(menu_by_id)) -> MenuRead:
    """
    \f
    :param menu_id:
    :return: menu
    """

    return menu


@router.patch(
    '/{menu_id}',
    response_model=MenuRead,
    status_code=status.HTTP_200_OK,
    summary='Обновить меню',
    responses={
        404: {
            'description': 'menu not found',
            'model': ErrorResponse
        }
    }
)
async def update_menu(
    menu_update: MenuUpdatePartial,
    background_tasks: BackgroundTasks,
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> MenuRead:
    """
    \f
    :param menu_update:
    :param menu_id:
    :param session:
    :return: menu
    """
    await create_background_task(
        background_tasks,
        redis.clear_cache,
        f'menu_{menu.id}',
        'all_menus',
        'all_menus_nested'
    )

    return await crud.update_menu_partial(
        session=session, menu=menu, menu_update=menu_update
    )


@router.delete(
    '/{menu_id}',
    status_code=status.HTTP_200_OK,
    summary='Удалить меню',
    responses={
        404: {
            'description': 'menu not found',
            'model': ErrorResponse
        },
        200: {
            'model': SuccessResponse
        }
    }
)
async def delete_menu(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    menu: Menu = Depends(menu_by_id),
) -> JSONResponse:
    """
    \f
    :param menu_id:
    :param session:
    :return: result
    """
    await create_background_task(background_tasks, clear_menu_cache, menu.id)

    return await crud.delete_menu(session, menu)
