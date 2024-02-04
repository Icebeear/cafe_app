from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Dish, SubMenu
from src.dish.schemas import DishCreate, DishRead, DishUpdatePartial


async def create_dish(
        session: AsyncSession,
        dish: DishCreate,
        submenu: SubMenu
) -> DishRead:
    query = (
        insert(Dish)
        .values(**dish.model_dump(), submenu_id=submenu.id)
        .returning(Dish)
    )
    result = await session.execute(query)
    await session.commit()
    return result.scalars().first()


async def get_dish_by_title(session: AsyncSession, dish_title: str) -> Dish:
    query = select(Dish).where(Dish.title == dish_title)
    result = await session.execute(query)
    return result.scalars().first()


async def get_dish_by_id(session: AsyncSession, dish_id: str) -> Dish:
    query = select(Dish).where(Dish.id == dish_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_dishes(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 100
) -> list[Dish]:
    query = select(Dish).offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def update_dish_partial(
    session: AsyncSession,
    dish: Dish,
    dish_update: DishUpdatePartial,
) -> Dish:
    for name, value in dish_update.model_dump(exclude_unset=True).items():
        setattr(dish, name, value)
    await session.commit()

    return dish


async def delete_dish(
    session: AsyncSession,
    dish: Dish,
) -> dict:
    await session.delete(dish)
    await session.commit()

    return {'status': True, 'message': 'The dish has been deleted'}
