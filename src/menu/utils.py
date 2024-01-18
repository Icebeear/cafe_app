from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings.database import get_async_session

from src.menu.models import Menu, SubMenu, Dish
from src.menu.crud import get_menu_by_id, get_submenu_by_id
import uuid

async def menu_by_id(
    menu_id: Annotated[str, Path],
    session: AsyncSession = Depends(get_async_session),
) -> Menu:
    result = await get_menu_by_id(session, menu_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"menu not found"
        )
    return result


async def submenu_by_id(
    submenu_id: Annotated[str, Path],
    session: AsyncSession = Depends(get_async_session),
) -> SubMenu:
    result = await get_submenu_by_id(session, submenu_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"submenu not found"
        )
    return result


async def change_count(
    menu: Menu,
    session: AsyncSession,
    submenu: SubMenu,
    increase_submenus: bool | None = None,
    increase_dishes: bool | None = None,
) -> None:
    
    if increase_submenus != None:
        menu.submenus_count += 1 if increase_submenus else -1 
    
    if increase_dishes != None:
        menu.dishes_count += 1 if increase_dishes else -1 
        submenu.dishes_count += 1 if increase_dishes else -1

    await session.commit()