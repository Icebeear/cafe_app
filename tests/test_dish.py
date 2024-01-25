from httpx import AsyncClient
import pytest 


'''Проверка crud для dish'''
@pytest.mark.asyncio
@pytest.mark.order(3)
async def test_dishes(ac: AsyncClient):
    menu = await ac.post(
        "/api/v1/menus/",
        json={
            "title": "menu 1",
            "description": "menu 1 description",
        },
    )
    assert menu.status_code == 201

    menu_id = menu.json()["id"]

    submenu = await ac.post(
        f"/api/v1/menus/{menu_id}/submenus/",
        json={
            "title": "submenu 1",
            "description": "description for submenu",
        }
    )
    assert submenu.status_code == 201 

    submenu_id = submenu.json()["id"]

    dish = await ac.post(
        f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/",
        json={
            "title": "dish 1",
            "description": "description for dish 1",
            "price": "7.5",
        }
    )
    assert dish.status_code == 201 

    dishes = await ac.get(
        f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/",
    )

    assert len(dishes.json()) == 1 

    response = await ac.get(
        f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish.json()['id']}",
    )

    assert response.status_code == 200 

    assert response.json()["title"] == "dish 1"
    
    response = await ac.patch(
        f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish.json()['id']}",
        json={
            "title": "new title for dish 1",
            "description": "new description for dish 1",
            "price": "20.0",
        }
    )

    assert response.status_code == 200 

    response = await ac.delete(
        f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish.json()['id']}",
    )

    assert response.status_code == 200 


    response = await ac.get(
        f"/api/v1/menus/{menu_id}/{submenu_id}/{dish.json()['id']}"
    )

    assert response.status_code == 404