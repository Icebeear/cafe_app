from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Menu, SubMenu
from src.submenu.schemas import SubMenuCreate, SubMenuUpdatePartial


async def get_submenu_by_id(
    session: AsyncSession,
    submenu_id: str,
) -> SubMenu:
    query = select(SubMenu).where(SubMenu.id == submenu_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_submenus(
    session: AsyncSession, menu: Menu, offset: int = 0, limit: int = 100
) -> list[SubMenu]:
    query = (
        select(SubMenu).where(SubMenu.menu_id == menu.id).offset(offset).limit(limit)
    )
    result = await session.execute(query)

    submenus = result.scalars().all()

    from src.submenu.services import count_dishes

    for sub_menu in submenus:
        sub_menu.dishes_count = await count_dishes(session, sub_menu.id)

    return submenus


async def create_submenu(
    session: AsyncSession,
    menu: Menu,
    submenu: SubMenuCreate,
) -> SubMenu:
    query = (
        insert(SubMenu)
        .values(**submenu.model_dump(), menu_id=menu.id)
        .returning(SubMenu)
    )
    result = await session.execute(query)
    await session.commit()
    return result.scalars().first()


async def update_submenu_partial(
    session: AsyncSession,
    submenu: SubMenu,
    submenu_update: SubMenuUpdatePartial,
) -> SubMenu:
    for name, value in submenu_update.model_dump(exclude_unset=True).items():
        setattr(submenu, name, value)
    await session.commit()

    return submenu


async def delete_submenu(
    session: AsyncSession,
    submenu: SubMenu,
) -> dict[str, bool | str]:
    await session.delete(submenu)
    await session.commit()

    return {'status': True, 'message': 'The submenu has been deleted'}


async def get_submenu_by_title(
    session: AsyncSession,
    submenu_title: str,
) -> SubMenu:
    query = select(SubMenu).where(SubMenu.title == submenu_title)
    result = await session.execute(query)
    return result.scalars().first()
