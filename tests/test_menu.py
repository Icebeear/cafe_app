import pytest
from fastapi import Request
from httpx import AsyncClient

from tests.utils import reverse

"""Проверка crud для menu"""


@pytest.mark.order(2)
class TestMenuAPI:
    @pytest.fixture
    async def menu_id(self, ac: AsyncClient, request: Request) -> str:
        menu_title = f'menu_for_submenu_{request.node.name}'

        url = reverse('get_menus')
        response = await ac.post(
            url,
            json={
                'title': menu_title,
                'description': 'menu 1 description',
            },
        )
        assert response.status_code == 201
        return response.json()['id']

    @pytest.mark.asyncio
    async def test_menu_create(self, ac: AsyncClient) -> None:
        url = reverse('create_menu')
        response = await ac.post(
            url,
            json={
                'title': 'menu 2',
                'description': 'menu 2 description',
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_menu_patch(self, ac: AsyncClient, menu_id: str) -> None:
        url = reverse('update_menu', menu_id=menu_id)
        response = await ac.patch(
            url,
            json={
                'title': 'new title for menu 3',
                'description': 'new description for menu 3',
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_menu_delete(self, ac: AsyncClient, menu_id: str) -> None:
        url = reverse('delete_menu', menu_id=menu_id)
        response = await ac.delete(
            url,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_menu_get_wrong(self, ac: AsyncClient) -> None:
        url = reverse('get_menu', menu_id='db37ad5e-04d6-4060-9ca2-f26549757f45')
        response = await ac.get(url)

        assert response.status_code == 404
        assert response.json()['detail'] == 'menu not found'

    @pytest.mark.asyncio
    async def test_menu_get_all(self, ac: AsyncClient) -> None:
        url = reverse('get_menus')
        response = await ac.get(url)

        assert response.status_code == 200
        assert len(response.json()) == 2
