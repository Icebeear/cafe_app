from httpx import AsyncClient
import pytest 

'''
Проверка кол-ва блюд и подменю в меню
'''
@pytest.mark.asyncio
@pytest.mark.order(4)
async def test_submenus_count_and_dishes_count(ac: AsyncClient):
    ''' create menu '''
    menu = await ac.post(
        "/api/v1/menus/",
        json={
            "title": "menu 1",
            "description": "cool menu",
        },
    )
    assert menu.status_code == 201

    ''' create submenu '''
    submenu = await ac.post(
        f"/api/v1/menus/{menu.json()['id']}/submenus/",
        json={
            "title": "submenu for test",
            "description": "awesome submenu",
        }
    )
    assert submenu.status_code == 201 

    ''' add 2 dishes '''
    dish1 = await ac.post(
        f"api/v1/menus/{menu.json()['id']}/submenus/{submenu.json()['id']}/dishes/",
        json={
            "title": "apple pie",
            "description": "so tasty",
            "price": "10.0",
        }
    )

    dish2 = await ac.post(
        f"api/v1/menus/{menu.json()['id']}/submenus/{submenu.json()['id']}/dishes/",
        json={
            "title": "coca cola",
            "description": "from usa",
            "price": "5.0",
        }
    )

    assert dish1.status_code == 201
    assert dish2.status_code == 201

    ''' check response '''
    response = await ac.get(
        f"/api/v1/menus/{menu.json()['id']}"
    )

    all_data = response.json()
    assert response.status_code == 200
    assert all_data["id"] == menu.json()["id"]
    assert all_data["title"] == "menu 1"
    assert all_data["description"] == "cool menu"
    assert all_data["submenus_count"] == 1
    assert all_data["dishes_count"] == 2
