import json

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Menu
from src.menu import crud
from src.menu.schemas import MenuCreate, MenuRead, MenuUpdatePartial
from src.menu.utils import clear_menu_cache, menu_by_id
from src.redis.utils import get_redis_client

r = get_redis_client()

router = APIRouter(tags=['Menu'], prefix='/menus')


@router.post(
    '/',
    response_model=MenuRead,
    status_code=status.HTTP_201_CREATED
)
async def create_menu(
    menu: MenuCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    \f
    :param menu:
    :param session:
    :return: new_menu
    """

    r.delete('all_menus')

    new_menu = await crud.create_menu(session, menu)

    return new_menu


@router.get(
    '/',
    response_model=list[MenuRead],
    status_code=status.HTTP_200_OK
)
async def get_menus(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 100,
):
    """
    \f
    :param session:
    :param offset:
    :param limit:
    :return: menus
    """

    cache = r.get('all_menus')

    if cache:
        return json.loads(cache)

    menus = await crud.get_menus(session, offset, limit)

    r.setex('all_menus', 3600, json.dumps(jsonable_encoder(menus)))

    return menus


@router.get(
    '/{menu_id}',
    response_model=MenuRead,
    status_code=status.HTTP_200_OK
)
async def get_menu(menu: Menu = Depends(menu_by_id)):
    """
    \f
    :param menu_id:
    :return: menu
    """

    return menu


@router.patch(
    '/{menu_id}',
    response_model=MenuRead,
    status_code=status.HTTP_200_OK
)
async def update_menu(
    menu_update: MenuUpdatePartial,
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    """
    \f
    :param menu_update:
    :param menu_id:
    :param session:
    :return: menu
    """
    r.delete(f'menu_{menu.id}')
    r.delete('all_menus')

    return await crud.update_menu_partial(
        session=session, menu=menu, menu_update=menu_update
    )


@router.delete('/{menu_id}', status_code=status.HTTP_200_OK)
async def delete_menu(
    session: AsyncSession = Depends(get_async_session),
    menu: Menu = Depends(menu_by_id),
):
    """
    \f
    :param menu_id:
    :param session:
    :return: result
    """
    await clear_menu_cache(menu.id)

    return await crud.delete_menu(session, menu)
