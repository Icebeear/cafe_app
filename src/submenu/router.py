
from fastapi import APIRouter, Depends,  status
from sqlalchemy.ext.asyncio import AsyncSession


from src.submenu.schemas import SubMenuCreate, SubMenuRead, SubMenuUpdatePartial
from src.core.database import get_async_session

from src.submenu import crud 
from src.core.models import Menu, SubMenu
from src.submenu.utils import submenu_by_id, check_unique_submenu
from src.menu.utils import menu_by_id



router = APIRouter(tags=["Submenu"], prefix="/menus/{menu_id}/submenus")


@router.post("/", response_model=SubMenuRead, status_code=status.HTTP_201_CREATED)
async def create_submenu(
    submenu: SubMenuCreate,
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session)
):
    
    await check_unique_submenu(submenu.title, session)
    sub_menu = await crud.create_submenu(session, menu, submenu)

    return sub_menu


@router.get("/", response_model=list[SubMenuRead], status_code=status.HTTP_200_OK)
async def get_submenus(
    session: AsyncSession = Depends(get_async_session),
    menu: Menu = Depends(menu_by_id),
):
    
    return await crud.get_submenus(session, menu)
   

@router.get("/{submenu_id}", response_model=SubMenuRead, status_code=status.HTTP_200_OK)
async def get_submenu(
    menu: Menu = Depends(menu_by_id),
    submenu: SubMenu = Depends(submenu_by_id),
):
    return submenu


@router.patch("/{submenu_id}", response_model=SubMenuRead, status_code=status.HTTP_200_OK)
async def update_menu(
    submenu_update: SubMenuUpdatePartial,
    submenu: SubMenu = Depends(submenu_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.update_submenu_partial(
        session=session, 
        submenu=submenu, 
        submenu_update=submenu_update
    )


@router.delete("/{submenu_id}", status_code=status.HTTP_200_OK)
async def delete_menu(
    menu: Menu = Depends(menu_by_id),
    session: AsyncSession = Depends(get_async_session),
    submenu: SubMenu = Depends(submenu_by_id),
) -> dict:
    
    return await crud.delete_submenu(session, submenu)