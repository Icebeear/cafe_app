from httpx import AsyncClient
import pytest


'''Проверка crud для menu'''
@pytest.mark.asyncio
@pytest.mark.order(1)
async def test_menu(ac: AsyncClient):

    menu = await ac.post(
        "/api/v1/menus/",
        json={
            "title": "menu 1",
            "description": "menu 1 description",
        },
    )
    assert menu.status_code == 201

    response = await ac.get(
        "api/v1/menus/"
    )

    assert len(response.json()) == 1

    response = await ac.patch(
        f"/api/v1/menus/{menu.json()['id']}",
        json={
            "title": "new title for menu 1",
            "description": "new description for menu 1",
        }
    )

    assert response.status_code == 200 

    response = await ac.delete(
        f"/api/v1/menus/{menu.json()['id']}",
    )

    assert response.status_code == 200 


    response = await ac.get(
        f"/api/v1/menus/{menu.json()['id']}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "menu not found"