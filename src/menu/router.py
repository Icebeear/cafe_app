
from fastapi import APIRouter, Depends,  status
from sqlalchemy.ext.asyncio import AsyncSession


from src.menu.schemas import MenuCreate, MenuUpdatePartial, MenuRead, Dish, SubMenuCreate, SubMenuRead
from src.settings.database import get_async_session

from src.menu import crud 
from src.menu.models import Menu, SubMenu, Dish
from src.menu.utils import menu_by_id, submenu_by_id, change_count

router = APIRouter(tags=["Cafe"],)

"""Menu views"""

@router.post("/menus", response_model=MenuRead, status_code=status.HTTP_201_CREATED)
async def create_menu(
    menu: MenuCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    new_menu = await crud.create_menu(session, menu)
    return new_menu


@router.get("/menus", response_model=list[MenuRead], status_code=status.HTTP_200_OK)
async def get_menus(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 100,
):
    menus = await crud.get_menus(session, offset, limit)

    return menus


@router.get("/menus/{menu_id}", response_model=MenuRead, status_code=status.HTTP_200_OK)
async def get_menu(
    menu: Menu = Depends(menu_by_id)
):
    return menu


@router.patch("/menus/{menu_id}", response_model=MenuRead, status_code=status.HTTP_200_OK)
async def update_menu(
    menu_update: MenuUpdatePartial,
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.update_menu_partial(
        session=session, 
        menu=menu, 
        menu_update=menu_update
    )
    

@router.delete("/menus/{menu_id}", status_code=status.HTTP_200_OK)
async def delete_menu(
    session: AsyncSession = Depends(get_async_session),
    menu: Menu = Depends(menu_by_id),
) -> None:
    
    await crud.delete_menu(session, menu)
    


'''Submenus views'''

@router.get("/menus/{menu_id}/submenus", status_code=status.HTTP_200_OK)
async def get_submenus(
    session: AsyncSession = Depends(get_async_session),
    menu: Menu = Depends(menu_by_id),
) -> list[SubMenuRead]:
    
    return await crud.get_submenus(session, menu)
   

@router.post("/menus/{menu_id}/submenus", response_model=MenuRead, status_code=status.HTTP_201_CREATED)
async def create_submenu(
    submenu: SubMenuCreate,
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session)
):
    
    sub_menu = await crud.create_submenu(session, menu, submenu)
    await change_count(menu=menu, submenu=sub_menu, session=session, increase_submenus=True)
    return sub_menu


@router.get("/menus/{menu_id}/submenus/{submenu_id}", response_model=SubMenuRead, status_code=status.HTTP_200_OK)
async def get_submenu(
    menu: Menu = Depends(menu_by_id),
    submenu: SubMenu = Depends(submenu_by_id),
):
    return submenu


@router.delete("/menus/{menu_id}/submenus/{submenu_id}", status_code=status.HTTP_200_OK)
async def delete_menu(
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session),
    submenu: SubMenu = Depends(submenu_by_id),
) -> None:
    
    await crud.delete_submenu(session, submenu)
    await change_count(menu, session, submenu, increase_submenus=False)