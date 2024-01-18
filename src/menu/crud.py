
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.menu.models import Menu, SubMenu, Dish

from src.menu.schemas import MenuCreate, MenuUpdatePartial, MenuRead, SubMenuCreate, SubMenuRead, Dish


'''Menu cruds'''
async def create_menu(session: AsyncSession, menu: MenuCreate) -> MenuRead:
    query = insert(Menu).values(**menu.model_dump()).returning(Menu)
    result = await session.execute(query)
    await session.commit()
    return result.scalars().first()


async def get_menus(session: AsyncSession, offset: int = 0, limit: int = 100) -> list[MenuRead]:
    query = select(Menu).offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


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
) -> None:
    await session.delete(menu)
    await session.commit()


'''Submenu cruds'''

async def get_submenu_by_id(
        session: AsyncSession,
        submenu_id: int,
) -> SubMenu | None:
    query = select(SubMenu).where(SubMenu.id == submenu_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_submenus(
        session: AsyncSession,
        menu: Menu,
) -> list[SubMenuRead]:
    query = select(SubMenu).where(SubMenu.menu_id == menu.id)
    result = await session.execute(query)
    return result.scalars().all()


async def create_submenu(
        session: AsyncSession,
        menu: Menu,
        submenu: SubMenuCreate,
) -> SubMenuRead:
    
    query = insert(SubMenu).values(**submenu.model_dump(), menu_id=menu.id).returning(SubMenu)
    result = await session.execute(query)
    await session.commit()
    return result.scalars().first()


async def delete_submenu(
        session: AsyncSession,
        submenu: SubMenu,
):
    await session.delete(submenu)
    await session.commit()
