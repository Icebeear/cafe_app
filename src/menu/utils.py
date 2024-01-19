from typing import Annotated
from sqlalchemy import insert, select
from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session

from src.core.models import Menu, SubMenu, Dish
from src.menu.crud import get_menu_by_id


async def menu_by_id(
    menu_id: Annotated[str, Path],
    session: AsyncSession = Depends(get_async_session),
) -> Menu:
    menu = await get_menu_by_id(session, menu_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"menu not found"
        )
    
    menu.submenus_count = await count_submenus(session, menu.id)
    menu.dishes_count = await count_dishes(session, menu.id)

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




