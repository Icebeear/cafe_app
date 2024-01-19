from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish
from src.dish.crud import get_dish_by_id, get_dish_by_title


async def dish_by_id(
    dish_id: Annotated[str, Path],
    session: AsyncSession = Depends(get_async_session),
) -> Dish:
    result = await get_dish_by_id(session, dish_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"dish not found"
        )
    return result


async def check_unique_dish(
    session: AsyncSession,
    dish_title: Annotated[str, Path],
) -> None:
    
    result = await get_dish_by_title(session, dish_title)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"dish cannot be in 2 submenus at the same time",
        )
