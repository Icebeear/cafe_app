from httpx import AsyncClient
import pytest 


'''Проверка crud для submenu'''
@pytest.mark.asyncio
@pytest.mark.order(2)
async def test_submenus(ac: AsyncClient):
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

    submenus = await ac.get(
        f"/api/v1/menus/{menu_id}/submenus/",
    )

    assert len(submenus.json()) == 1 

    response = await ac.get(
        f"/api/v1/menus/{menu_id}/submenus/{submenu.json()['id']}",
    )

    assert response.status_code == 200 

    assert response.json()["title"] == "submenu 1"
    
    response = await ac.patch(
        f"/api/v1/menus/{menu_id}/submenus/{submenu.json()['id']}",
        json={
            "title": "new title for submenu 1",
            "description": "new description for submenu 1",
        }
    )

    assert response.status_code == 200 

    response = await ac.delete(
        f"/api/v1/menus/{menu_id}/submenus/{submenu.json()['id']}",
    )

    assert response.status_code == 200 


    response = await ac.get(
        f"/api/v1/menus/{menu_id}/{submenu.json()['id']}"
    )

    assert response.status_code == 404
    