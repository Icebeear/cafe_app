from httpx import AsyncClient
import pytest


"""Проверка crud для menu"""


@pytest.mark.order(2)
class TestMenuAPI:
    @pytest.fixture
    async def menu_id(self, ac: AsyncClient, request):
        menu_title = f"menu_for_submenu_{request.node.name}"

        response = await ac.post(
            "/api/v1/menus/",
            json={
                "title": menu_title,
                "description": "menu 1 description",
            },
        )
        assert response.status_code == 201
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_menu_create(self, ac: AsyncClient):
        response = await ac.post(
            "/api/v1/menus/",
            json={
                "title": "menu 2",
                "description": "menu 2 description",
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_menu_patch(self, ac: AsyncClient, menu_id):
        response = await ac.patch(
            f"/api/v1/menus/{menu_id}",
            json={
                "title": "new title for menu 3",
                "description": "new description for menu 3",
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_menu_delete(self, ac: AsyncClient, menu_id):
        response = await ac.delete(
            f"/api/v1/menus/{menu_id}",
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_menu_get_wrong(self, ac: AsyncClient):
        response = await ac.get(f"/api/v1/menus/db37ad5e-04d6-4060-9ca2-f26549757f45")

        assert response.status_code == 404
        assert response.json()["detail"] == "menu not found"

    @pytest.mark.asyncio
    async def test_menu_get_all(self, ac: AsyncClient):
        response = await ac.get("api/v1/menus/")

        assert response.status_code == 200
        assert len(response.json()) == 3
