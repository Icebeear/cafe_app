from httpx import AsyncClient
import pytest


"""Проверка crud для dish"""


@pytest.mark.order(4)
class TestDishAPI:
    @pytest.fixture
    async def dish_fixture(self, ac: AsyncClient, request):
        menu_title = f"menu_for_submenu_{request.node.name}"
        submenu_title = f"submenu_for_test_{request.node.name}"
        dish_title = f"dish_for_test_{request.node.name}"

        menu = await ac.post(
            "/api/v1/menus/",
            json={
                "title": menu_title,
                "description": "menu for submenu description",
            },
        )

        assert menu.status_code == 201
        menu_id = menu.json()["id"]

        submenu = await ac.post(
            f"/api/v1/menus/{menu_id}/submenus/",
            json={
                "title": submenu_title,
                "description": "description for submenu 1",
            },
        )
        assert submenu.status_code == 201
        submenu_id = submenu.json()["id"]

        dish = await ac.post(
            f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/",
            json={
                "title": dish_title,
                "description": "description for submenu 1",
                "price": "10",
            },
        )
        assert dish.status_code == 201
        dish_id = dish.json()["id"]

        return menu_id, submenu_id, dish_id

    @pytest.mark.asyncio
    async def test_dish_create(self, ac: AsyncClient, dish_fixture):
        dish = await ac.post(
            f"/api/v1/menus/{dish_fixture[0]}/submenus/{dish_fixture[1]}/dishes/",
            json={
                "title": "dish 1",
                "description": "description for dish 1",
                "price": "7.5",
            },
        )
        assert dish.status_code == 201

    @pytest.mark.asyncio
    async def test_dish_patch(self, ac: AsyncClient, dish_fixture):
        response = await ac.patch(
            f"/api/v1/menus/{dish_fixture[0]}/submenus/{dish_fixture[1]}/dishes/{dish_fixture[2]}",
            json={
                "title": "new title for dish 1",
                "description": "new description for dish 1",
                "price": "20.0",
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dish_delete(self, ac: AsyncClient, dish_fixture):
        response = await ac.delete(
            f"/api/v1/menus/{dish_fixture[0]}/submenus/{dish_fixture[1]}/dishes/{dish_fixture[2]}",
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dish_get_all(self, ac: AsyncClient, dish_fixture):
        dishes = await ac.get(
            f"/api/v1/menus/{dish_fixture[0]}/submenus/{dish_fixture[1]}/dishes/",
        )

        assert len(dishes.json()) == 4
