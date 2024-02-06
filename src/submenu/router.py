from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.core.database import get_async_session
from src.core.models import Menu, SubMenu
from src.core.schemas import ErrorResponse, SuccessResponse
from src.menu.services import menu_by_id
from src.redis.utils import redis
from src.submenu import crud
from src.submenu.schemas import SubMenuCreate, SubMenuRead, SubMenuUpdatePartial
from src.submenu.services import (
    check_unique_submenu,
    clear_submenu_cache,
    load_all_submenus,
    submenu_by_id,
)

router = APIRouter(tags=['Submenu'], prefix='/menus/{menu_id}/submenus')


@router.post(
    '/',
    response_model=SubMenuRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать подменю',
    responses={
        409: {
            'description': 'submenu cannot be in 2 menus at the same time',
            'model': ErrorResponse
        }
    }
)
async def create_submenu(
    submenu: SubMenuCreate,
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> SubMenuRead:
    """
    \f
    :param submenu:
    :param menu_id:
    :param session:
    :return: sub_menu
    """
    await check_unique_submenu(submenu.title, session)

    redis.clear_cache('all_menus', 'all_submenus', f'menu_{menu.id}')

    sub_menu = await crud.create_submenu(session, menu, submenu)

    return sub_menu


@router.get(
    '/',
    response_model=list[SubMenuRead],
    status_code=status.HTTP_200_OK,
    summary='Получить все подменю'
)
async def get_submenus(
    session: AsyncSession = Depends(get_async_session),
    menu: Menu = Depends(menu_by_id),
    offset: int = 0,
    limit: int = 100,
) -> list[SubMenuRead]:
    """
    \f
    :param session:
    :param menu_id:
    :return: submenus
    """

    submenus = await load_all_submenus(session, menu, offset, limit)

    return submenus


@router.get(
    '/{submenu_id}',
    response_model=SubMenuRead,
    status_code=status.HTTP_200_OK,
    summary='Получить подменю',
    responses={
        404: {
            'description': 'submenu not found',
            'model': ErrorResponse
        }
    }
)
async def get_submenu(
    submenu: SubMenu = Depends(submenu_by_id),
) -> SubMenuRead:
    """
    \f
    :param menu_id:
    :param submenu_id:
    :return: submenu
    """

    return submenu


@router.patch(
    '/{submenu_id}',
    response_model=SubMenuRead,
    status_code=status.HTTP_200_OK,
    summary='Обновить подменю',
    responses={
        404: {
            'description': 'submenu not found',
            'model': ErrorResponse
        }
    }
)
async def update_submenu(
    submenu_update: SubMenuUpdatePartial,
    submenu: SubMenu = Depends(submenu_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> SubMenuRead:
    """
    \f
    :param menu_id:
    :param submenu_update:
    :param submenu_id:
    :param session:
    :return: submenu
    """

    redis.clear_cache(f'{submenu.menu_id}_submenu_{submenu.id}', 'all_submenus')

    return await crud.update_submenu_partial(
        session=session, submenu=submenu, submenu_update=submenu_update
    )


@router.delete(
    '/{submenu_id}',
    status_code=status.HTTP_200_OK,
    summary='Удалить подменю',
    responses={
        404: {
            'description': 'submenu not found',
            'model': ErrorResponse
        },
        200: {
            'model': SuccessResponse
        }
    }
)
async def delete_submenu(
    session: AsyncSession = Depends(get_async_session),
    submenu: SubMenu = Depends(submenu_by_id),
) -> JSONResponse:
    """
    \f
    :param menu_id:
    :param session:
    :param submenu_id:
    :return: result
    """

    await clear_submenu_cache(submenu.menu_id, submenu.id)

    return await crud.delete_submenu(session, submenu)
