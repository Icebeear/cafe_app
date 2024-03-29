import json
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy import func, select
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_async_session
from src.core.models import Dish, Menu, SubMenu
from src.menu import crud
from src.menu.crud import get_menu_by_id, get_menu_by_title
from src.menu.schemas import MenuRead, MenuReadNested
from src.redis.utils import redis

r = redis.get_redis_client()


async def menu_by_id(
    menu_id: Annotated[UUID4, Path],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Menu:
    cache = r.get(f'menu_{menu_id}')

    if cache and request.method == 'GET':
        return MenuRead(**json.loads(cache))

    menu = await get_menu_by_id(session, menu_id)

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='menu not found'
        )

    submenus_dishes = await get_submenus_dishes(session, menu.id)

    menu.submenus_count = submenus_dishes.total_submenus
    menu.dishes_count = submenus_dishes.total_dishes

    if request.method == 'GET':
        r.setex(f'menu_{menu.id}', 600, json.dumps(jsonable_encoder(menu)))

    return menu


async def check_unique_menu(
    menu_title: Annotated[str, Path],
    session: AsyncSession,
) -> None:
    result = await get_menu_by_title(session, menu_title)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='menu with that title already exists',
        )


async def get_submenus_dishes(
    session: AsyncSession,
    menu_id: Annotated[str, Path],
) -> Row:
    query = (
        select(
            func.count(func.distinct(SubMenu.id)).label('total_submenus'),
            func.count(func.distinct(Dish.id)).label('total_dishes'),
        )
        .select_from(Menu)
        .outerjoin(SubMenu, Menu.id == SubMenu.menu_id)
        .outerjoin(Dish, SubMenu.id == Dish.submenu_id)
        .where(Menu.id == menu_id)
        .group_by(Menu.id, Menu.title)
    )

    result = await session.execute(query)

    row = result.fetchone()

    return row


def clear_menu_cache(menu_id: str) -> None:
    redis.clear_main_cache()

    redis.clear_cache(f'menu_{menu_id}')

    submenu_keys = r.keys(f'{menu_id}*')

    # clear all submenus for target menu
    submenus = []
    for key in submenu_keys:
        r.delete(key)
        submenus.append(f"{key.split('_')[-1]}*")

    # find all dishes for all submenus
    dish_keys = []
    for submenu in submenus:
        dish_keys.extend(r.keys(submenu))

    # clear all dishes
    if dish_keys:
        redis.clear_cache(dish_keys)


async def load_all_menus(session: AsyncSession, offset: int, limit: int) -> list[Menu]:
    cache = r.get('all_menus')
    params = r.get('menus_params')

    if cache and params == f'{offset}_{limit}':
        return json.loads(cache)

    menus = await crud.get_menus(session, offset, limit)

    r.setex('all_menus', 3600, json.dumps(jsonable_encoder(menus)))
    r.setex('menus_params', 3600, f'{offset}_{limit}')

    return menus


async def load_all_menus_nested(session: AsyncSession, offset: int, limit: int) -> list[MenuReadNested]:
    cache = r.get('all_menus_nested')
    params = r.get('menus_nested_params')

    if cache and params == f'{offset}_{limit}':
        return json.loads(cache)

    query = select(Menu).options(
        selectinload(Menu.submenus).selectinload(SubMenu.dishes)
    ).offset(offset).limit(limit)

    result = await session.execute(query)

    nested_menus = result.scalars().all()

    r.setex('all_menus_nested', 6000, json.dumps(jsonable_encoder(nested_menus)))
    r.setex('menus_nested_params', 3600, f'{offset}_{limit}')

    return nested_menus
