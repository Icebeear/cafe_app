from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish, SubMenu
from src.submenu.crud import get_submenu_by_id, get_submenu_by_title


async def submenu_by_id(
    submenu_id: Annotated[str, Path],
    session: AsyncSession = Depends(get_async_session),
) -> SubMenu:
    submenu = await get_submenu_by_id(session, submenu_id)
    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"submenu not found"
        )

    submenu.dishes_count = await count_dishes(session, submenu_id)

    return submenu


async def check_unique_submenu(
    submenu_title: Annotated[str, Path],
    session: AsyncSession,
) -> None:
    result = await get_submenu_by_title(session, submenu_title)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"submenu cannot be in 2 menus at the same time",
        )


async def count_dishes(
    session: AsyncSession,
    submenu_id: str,
) -> int:
    query = select(Dish).where(Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    return len(result.scalars().all())
