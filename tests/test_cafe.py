from httpx import AsyncClient
import pytest

"""
Проверка кол-ва блюд и подменю в меню
"""


@pytest.mark.order(1)
class TestSubMenuDishAPI:
    @pytest.mark.asyncio
    async def test_mainmenu_create(self, ac: AsyncClient):
        global menu_id
        response = await ac.post(
            "/api/v1/menus/",
            json={
                "title": "main menu",
                "description": "main menu description",
            },
        )
        assert response.status_code == 201

        menu_id = response.json()["id"]

    @pytest.mark.asyncio
    async def test_submenu_create(self, ac: AsyncClient):
        global submenu_id
        submenu = await ac.post(
            f"/api/v1/menus/{menu_id}/submenus/",
            json={
                "title": "submenu for testing",
                "description": "awesome submenu",
            },
        )
        assert submenu.status_code == 201
        submenu_id = submenu.json()["id"]

    """ add 2 dishes """

    @pytest.mark.asyncio
    async def test_dish_create_1(self, ac: AsyncClient):
        response = await ac.post(
            f"api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/",
            json={
                "title": "apple pie",
                "description": "so tasty",
                "price": "10.0",
            },
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_dish_create_2(self, ac: AsyncClient):
        response = await ac.post(
            f"api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/",
            json={
                "title": "coca cola",
                "description": "from usa",
                "price": "5.0",
            },
        )

        assert response.status_code == 201

    """ check response """

    @pytest.mark.asyncio
    async def test_final_response(self, ac: AsyncClient):
        response = await ac.get(f"/api/v1/menus/{menu_id}")

        all_data = response.json()
        assert response.status_code == 200
        assert all_data["id"] == menu_id
        assert all_data["title"] == "main menu"
        assert all_data["description"] == "main menu description"
        assert all_data["submenus_count"] == 1
        assert all_data["dishes_count"] == 2
