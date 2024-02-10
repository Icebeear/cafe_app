import pytest
from httpx import AsyncClient

"""
Проверка кол-ва блюд и подменю в меню
"""

menu_id: int
submenu_id: int


@pytest.mark.order(1)
class TestSubMenuDishAPI:
    """create menu"""

    @pytest.mark.asyncio
    async def test_mainmenu_create(self, ac: AsyncClient) -> None:
        global menu_id
        response = await ac.post(
            '/api/v1/menus/',
            json={
                'title': 'main menu',
                'description': 'main menu description',
            },
        )
        assert response.status_code == 201

        menu_id = response.json()['id']

    """ create submenu """

    @pytest.mark.asyncio
    async def test_mainsubmenu_create(self, ac: AsyncClient) -> None:
        global submenu_id
        response = await ac.post(
            f'/api/v1/menus/{menu_id}/submenus/',
            json={
                'title': 'submenu for testing',
                'description': 'awesome submenu',
            },
        )
        assert response.status_code == 201
        submenu_id = response.json()['id']

    """ create 1 dish """

    @pytest.mark.asyncio
    async def test_dish_create_1(self, ac: AsyncClient) -> None:
        response = await ac.post(
            f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/',
            json={
                'title': 'apple pie',
                'description': 'so tasty',
                'price': '10.0',
            },
        )

        assert response.status_code == 201

    """ create 2 dish """

    @pytest.mark.asyncio
    async def test_dish_create_2(self, ac: AsyncClient) -> None:
        response = await ac.post(
            f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/',
            json={
                'title': 'coca cola',
                'description': 'from usa',
                'price': '5.0',
            },
        )

        assert response.status_code == 201

    """ check target menu """

    @pytest.mark.asyncio
    async def test_mainmenu_get(self, ac: AsyncClient) -> None:
        response = await ac.get(f'/api/v1/menus/{menu_id}')

        all_data = response.json()
        assert response.status_code == 200
        assert all_data['id'] == menu_id
        assert all_data['title'] == 'main menu'
        assert all_data['description'] == 'main menu description'
        assert all_data['submenus_count'] == 1
        assert all_data['dishes_count'] == 2

    """ check nested menus """

    @pytest.mark.asyncio
    async def test_menus_nested_get(self, ac: AsyncClient) -> None:
        response = await ac.get('/api/v1/menus/nested')

        all_data = response.json()
        assert response.status_code == 200
        assert len(all_data) == 1
        assert len(all_data[0]['submenus']) == 1
        assert len(all_data[0]['submenus'][0]['dishes']) == 2

    """ check target submenu """

    @pytest.mark.asyncio
    async def test_mainsubmenu_get(self, ac: AsyncClient) -> None:
        response = await ac.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')

        all_data = response.json()
        assert response.status_code == 200
        assert all_data['id'] == submenu_id
        assert all_data['title'] == 'submenu for testing'
        assert all_data['description'] == 'awesome submenu'
        assert all_data['dishes_count'] == 2

    """ delete submenu """

    @pytest.mark.asyncio
    async def test_mainsubmenu_delete(self, ac: AsyncClient) -> None:
        response = await ac.delete(
            f'/api/v1/menus/{menu_id}/submenus/{submenu_id}',
        )

        assert response.status_code == 200

    """ check nested menus """

    @pytest.mark.asyncio
    async def test_menus_nested_get2(self, ac: AsyncClient) -> None:
        response = await ac.get('/api/v1/menus/nested')

        all_data = response.json()
        assert response.status_code == 200
        assert len(all_data) == 1
        assert len(all_data[0]['submenus']) == 0

    """ check all submenus """

    @pytest.mark.asyncio
    async def test_mainsubmenu_get_all(self, ac: AsyncClient) -> None:
        response = await ac.get(
            f'/api/v1/menus/{menu_id}/submenus/',
        )

        assert response.status_code == 200
        assert response.json() == []

    """ check all dishes """

    @pytest.mark.asyncio
    async def test_dishes_get_all(self, ac: AsyncClient) -> None:
        response = await ac.get(
            f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/',
        )

        assert response.status_code == 200
        assert response.json() == []

    """ check target menu """

    @pytest.mark.asyncio
    async def test_mainmenu_get_2(self, ac: AsyncClient) -> None:
        response = await ac.get(f'/api/v1/menus/{menu_id}')

        all_data = response.json()
        assert response.status_code == 200
        assert all_data['id'] == menu_id
        assert all_data['title'] == 'main menu'
        assert all_data['description'] == 'main menu description'
        assert all_data['submenus_count'] == 0
        assert all_data['dishes_count'] == 0

    """ delete menu """

    @pytest.mark.asyncio
    async def test_mainmenu_delete(self, ac: AsyncClient) -> None:
        response = await ac.delete(
            f'/api/v1/menus/{menu_id}',
        )

        assert response.status_code == 200

    """ check all menus """

    @pytest.mark.asyncio
    async def test_mainmenu_get_all(self, ac: AsyncClient) -> None:
        response = await ac.get('api/v1/menus/')

        assert response.status_code == 200
        assert response.json() == []

    """ check nested menus """

    @pytest.mark.asyncio
    async def test_menus_nested_get3(self, ac: AsyncClient) -> None:
        response = await ac.get('/api/v1/menus/nested')

        all_data = response.json()
        assert response.status_code == 200
        assert len(all_data) == 0
