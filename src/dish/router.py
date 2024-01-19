from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.models import Dish, Menu, SubMenu
from src.dish import crud
from src.dish.schemas import DishCreate, DishRead, DishUpdatePartial
from src.dish.utils import check_unique_dish, dish_by_id
from src.menu.utils import menu_by_id
from src.submenu.utils import submenu_by_id

router = APIRouter(
    tags=["Dish"], prefix="/menus/{menu_id}/submenus/{submenu_id}/dishes"
)


@router.post("/", response_model=DishRead, status_code=status.HTTP_201_CREATED)
async def create_dish(
    dish: DishCreate,
    menu: Menu = Depends(menu_by_id),
    submenu: SubMenu = Depends(submenu_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    await check_unique_dish(session, dish.title)

    new_dish = await crud.create_dish(session, dish, submenu)

    return new_dish


@router.get(
    "/", 
    response_model=list[DishRead], 
    status_code=status.HTTP_200_OK
)
async def get_dishes(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 100,
):
    dishes = await crud.get_dishes(session, offset, limit)

    return dishes


@router.get(
    "/{dish_id}", 
    response_model=DishRead, 
    status_code=status.HTTP_200_OK
)
async def get_dish(
    session: AsyncSession = Depends(get_async_session),
    dish: Dish = Depends(dish_by_id),
):
    return dish


@router.patch(
    "/{dish_id}", 
    response_model=DishRead, 
    status_code=status.HTTP_200_OK
)
async def update_menu(
    dish_update: DishUpdatePartial,
    dish: Dish = Depends(dish_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.update_dish_partial(
        session=session, dish=dish, dish_update=dish_update
    )


@router.delete("/{dish_id}", status_code=status.HTTP_200_OK)
async def delete_menu(
    dish: Dish = Depends(dish_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.delete_dish(session, dish)
