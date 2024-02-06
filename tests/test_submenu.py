import pytest
from fastapi import Request
from httpx import AsyncClient

"""Проверка crud для submenu"""


@pytest.mark.order(3)
class TestSubMenuAPI:
    @pytest.fixture
    async def submenu_fixture(self, ac: AsyncClient, request: Request) -> list[str]:
        menu_title = f'menu_for_submenu_{request.node.name}'
        submenu_title = f'submenu_for_test_{request.node.name}'

        menu = await ac.post(
            '/api/v1/menus/',
            json={
                'title': menu_title,
                'description': 'menu for submenu description',
            },
        )

        assert menu.status_code == 201
        menu_id = menu.json()['id']

        submenu = await ac.post(
            f'/api/v1/menus/{menu_id}/submenus/',
            json={
                'title': submenu_title,
                'description': 'description for submenu 1',
            },
        )
        assert submenu.status_code == 201
        submenu_id = submenu.json()['id']

        return [menu_id, submenu_id]

    @pytest.mark.asyncio
    async def test_submenu_create(self, ac: AsyncClient, submenu_fixture: list[str]) -> None:
        respsonse = await ac.post(
            f'/api/v1/menus/{submenu_fixture[0]}/submenus/',
            json={
                'title': 'submenu 2',
                'description': 'description for submenu 2',
            },
        )
        assert respsonse.status_code == 201

    @pytest.mark.asyncio
    async def test_submenu_patch(self, ac: AsyncClient, submenu_fixture: list[str]) -> None:
        response = await ac.patch(
            f'/api/v1/menus/{submenu_fixture[0]}/submenus/{submenu_fixture[1]}',
            json={
                'title': 'new title for submenu 1',
                'description': 'new description for submenu 1',
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_submenu_delete(self, ac: AsyncClient, submenu_fixture: list[str]) -> None:
        response = await ac.delete(
            f'/api/v1/menus/{submenu_fixture[0]}/submenus/{submenu_fixture[1]}',
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_submenu_get_all(self, ac: AsyncClient, submenu_fixture: list[str]) -> None:
        submenus = await ac.get(
            f'/api/v1/menus/{submenu_fixture[0]}/submenus/',
        )

        assert len(submenus.json()) == 1
