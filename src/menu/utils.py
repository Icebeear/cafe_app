from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish, Menu, SubMenu
from src.menu.crud import get_menu_by_id

from sqlalchemy.orm import joinedload


async def menu_by_id(
    menu_id: Annotated[str, Path],
    session: AsyncSession = Depends(get_async_session),
) -> Menu:
    menu = await get_menu_by_id(session, menu_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"menu not found"
        )

    query = (
        select(
            func.count(func.distinct(SubMenu.id)).label('total_submenus'),
            func.count(func.distinct(Dish.id)).label('total_dishes')
        )
        .select_from(Menu)
        .outerjoin(SubMenu, Menu.id == SubMenu.menu_id)
        .outerjoin(Dish, SubMenu.id == Dish.submenu_id)
        .where(Menu.id == menu_id)
        .group_by(Menu.id, Menu.title)
    )

    result = await session.execute(query)

    result = result.fetchall()[0]

    menu.submenus_count = result[0] 
    menu.dishes_count = result[1] 

    return menu


async def count_submenus(
    session: AsyncSession,
    menu_id: str,
) -> int:
    query = select(SubMenu).where(SubMenu.menu_id == menu_id)
    result = await session.execute(query)
    return len(result.scalars().all())


async def count_dishes(
    session: AsyncSession,
    menu_id: str,
) -> int:
    query = select(Dish).join(SubMenu).where(SubMenu.menu_id == menu_id)
    result = await session.execute(query)
    return len(result.scalars().all())
