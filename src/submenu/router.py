import json

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Menu, SubMenu
from src.menu.utils import menu_by_id
from src.redis.utils import get_redis_client
from src.submenu import crud
from src.submenu.schemas import SubMenuCreate, SubMenuRead, SubMenuUpdatePartial
from src.submenu.utils import check_unique_submenu, clear_submenu_cache, submenu_by_id

r = get_redis_client()
router = APIRouter(tags=['Submenu'], prefix='/menus/{menu_id}/submenus')


@router.post(
    '/',
    response_model=SubMenuRead,
    status_code=status.HTTP_201_CREATED
)
async def create_submenu(
    submenu: SubMenuCreate,
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    """
    \f
    :param submenu:
    :param menu_id:
    :param session:
    :return: sub_menu
    """
    await check_unique_submenu(submenu.title, session)

    r.delete('all_menus')
    r.delete('all_submenus')
    r.delete(f'menu_{menu.id}')

    sub_menu = await crud.create_submenu(session, menu, submenu)

    return sub_menu


@router.get(
    '/',
    response_model=list[SubMenuRead],
    status_code=status.HTTP_200_OK
)
async def get_submenus(
    session: AsyncSession = Depends(get_async_session),
    menu: Menu = Depends(menu_by_id),
    offset: int = 0,
    limit: int = 100,
):
    """
    \f
    :param session:
    :param menu_id:
    :return: submenus
    """
    cache = r.get('all_submenus')

    if cache:
        return json.loads(cache)

    sub_menus = await crud.get_submenus(session, menu, offset, limit)

    r.setex('all_submenus', 3600, json.dumps(jsonable_encoder(sub_menus)))

    return sub_menus


@router.get(
    '/{submenu_id}',
    response_model=SubMenuRead,
    status_code=status.HTTP_200_OK
)
async def get_submenu(
    submenu: SubMenu = Depends(submenu_by_id),
):
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
    status_code=status.HTTP_200_OK
)
async def update_submenu(
    submenu_update: SubMenuUpdatePartial,
    submenu: SubMenu = Depends(submenu_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    """
    \f
    :param menu_id:
    :param submenu_update:
    :param submenu_id:
    :param session:
    :return: submenu
    """

    r.delete(f'{submenu.menu_id}_submenu_{submenu.id}')
    r.delete('all_submenus')

    return await crud.update_submenu_partial(
        session=session, submenu=submenu, submenu_update=submenu_update
    )


@router.delete('/{submenu_id}', status_code=status.HTTP_200_OK)
async def delete_submenu(
    session: AsyncSession = Depends(get_async_session),
    submenu: SubMenu = Depends(submenu_by_id),
):
    """
    \f
    :param menu_id:
    :param session:
    :param submenu_id:
    :return: result
    """

    await clear_submenu_cache(submenu.menu_id, submenu.id)

    return await crud.delete_submenu(session, submenu)
