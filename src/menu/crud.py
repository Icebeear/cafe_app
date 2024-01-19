
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Menu

from src.menu.schemas import MenuCreate, MenuUpdatePartial, MenuRead

async def create_menu(session: AsyncSession, menu: MenuCreate) -> MenuRead:
    query = insert(Menu).values(**menu.model_dump()).returning(Menu)
    result = await session.execute(query)
    await session.commit()
    return result.scalars().first()


async def get_menus(session: AsyncSession, offset: int = 0, limit: int = 100) -> list[MenuRead]:
    query = select(Menu).offset(offset).limit(limit)
    result = await session.execute(query)
    menus =  result.scalars().all()

    from src.menu.utils import count_submenus, count_dishes
    
    for menu in menus:
        menu.submenus_count = await count_submenus(session, menu.id)
        menu.dishes_count = await count_dishes(session, menu.id)

    return menus 


async def get_menu_by_id(session: AsyncSession, menu_id) -> Menu | None:
    query = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(query)
    return result.scalars().first()


async def update_menu_partial(
        session: AsyncSession, 
        menu: Menu,
        menu_update: MenuUpdatePartial | None = None,
) -> Menu:

    for name, value in menu_update.model_dump(exclude_unset=True).items():
        setattr(menu, name, value)
    await session.commit()

    return menu
    
    
async def delete_menu(
        session: AsyncSession,
        menu: Menu,
) -> dict:
    await session.delete(menu)
    await session.commit()

    return {
        "status": True,
        "message": "The menu has been deleted"
    }


