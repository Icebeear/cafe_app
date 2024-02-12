import asyncio
import json
from typing import Any

import aiohttp
import pandas as pd
from aiohttp import ClientResponse
from fastapi.encoders import jsonable_encoder
from google.oauth2 import service_account
from googleapiclient.discovery import build

from src.redis.utils import redis

base_url: str
dishes_ids: list[str]
discounts: dict[str, float]
menus_ids: list[str]
google_dishes_ids: list[str]
google_menus_ids: list[str]
spreadsheet_id: str
sheet: Any


async def post_request(url: str, json: dict[str, Any]) -> ClientResponse:
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json=json)
        return response


async def patch_request(url: str, json: dict[str, Any]) -> ClientResponse:
    async with aiohttp.ClientSession() as session:
        response = await session.patch(url, json=json)
        return response


async def delete_request(url: str) -> ClientResponse:
    async with aiohttp.ClientSession() as session:
        response = await session.delete(url)
        return response


async def fetch(url: str) -> ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return response


async def update_sheet_values(table: str, row: int, values: str) -> None:
    sheet.values().update(
        spreadsheetId=spreadsheet_id,
        range=f'sheet1!{table}{row + 1}',
        valueInputOption='RAW',
        body={'values': [[values]]}
    ).execute()


async def update_menu(menu_id: str, google_menu: dict[str, Any]) -> None:
    response = await fetch(f'{base_url}/menus/{menu_id}')

    '''
    Идем в бд по id меню из таблицы, если оно есть, сразу патчим
    и обновляем зависимости.
    '''
    if isinstance(response, dict):

        await patch_request(f'{base_url}/menus/{menu_id}', json={
            'title': google_menu['title'],
            'description': google_menu['description'],
        })

        await update_all_data(menu_id, google_menu)

    else:
        '''
        Если не нашли по id (значит меню либо нету, либо до этого когда то создавалось в бд вручную),
        пытаемся создать, если получилось,
        создаем все остальное из таблицы. Если нет, значит в бд уже лежит меню с таким названием.
        Находим его по названию, берем id и идем обновлять все зависимости.
        '''

        response = await post_request(f'{base_url}/menus/', json={
            'title': google_menu['title'],
            'description': google_menu['description'],
        })

        if response.status == 201:
            data = await response.json()
            menu_id = data['id']

            await create_all_data(menu_id, google_menu)

        elif response.status == 409:
            all_menus = await fetch(f'{base_url}/menus/')
            menu_id = [menu['id'] for menu in all_menus if google_menu['title'] == menu['title']][0]

            await update_all_data(menu_id, google_menu)


async def create_all_data(menu_id: str, google_menu: dict[str, Any]):
    await update_sheet_values('A', google_menu['index'], menu_id)

    for google_submenu in google_menu['submenus']:

        response = await post_request(f'{base_url}/menus/{menu_id}/submenus/', json={
            'title': google_submenu['title'],
            'description': google_submenu['description'],
        })

        if response.status == 201:
            data = await response.json()
            submenu_id = data['id']

            await update_sheet_values('B', google_submenu['index'], submenu_id)

            for google_dish in google_submenu['dishes']:

                response = await post_request(f'{base_url}/menus/{menu_id}/submenus/{submenu_id}/dishes/', json={
                    'title': google_dish['title'],
                    'description': google_dish['description'],
                    'price': google_dish['price'],
                })

                data = await response.json()
                dish_id = data['id']

                await update_sheet_values('C', google_dish['index'], dish_id)


async def update_all_data(menu_id: str, google_menu: dict[str, Any]):
    submenus = await fetch(f'{base_url}/menus/{menu_id}/submenus/')

    submenus_ids = [submenu['id'] for submenu in submenus] or []
    submenus_titles = [submenu['title'] for submenu in submenus] or []

    google_submenus_ids = []

    for google_submenu in google_menu['submenus']:
        google_submenu_id = google_submenu['id']
        google_submenu_title = google_submenu['title']

        if google_submenu_id in submenus_ids:

            await patch_request(f'{base_url}/menus/{menu_id}/submenus/{google_submenu_id}', json={
                'title': google_submenu['title'],
                'description': google_submenu['description'],
            })

        elif google_submenu_title in submenus_titles:

            submenu_id = [submenu['id'] for submenu in submenus if submenu['title'] == google_submenu_title][0]

            await patch_request(f'{base_url}/menus/{menu_id}/submenus/{submenu_id}', json={
                'title': google_submenu['title'],
                'description': google_submenu['description'],
            })

            google_submenu_id = submenu_id

        else:

            response = await post_request(f'{base_url}/menus/{menu_id}/submenus/', json={
                'title': google_submenu['title'],
                'description': google_submenu['description'],
            })

            data = await response.json()
            google_submenu_id = data['id']

        await update_sheet_values('B', google_submenu['index'], google_submenu_id)

        for google_dish in google_submenu['dishes']:
            google_dish_id = google_dish['id']

            if google_dish_id in dishes_ids:

                await patch_request(f'{base_url}/menus/{menu_id}/submenus/{google_submenu_id}/dishes/{google_dish_id}', json={
                    'title': google_dish['title'],
                    'description': google_dish['description'],
                    'price': google_dish['price'],
                })

            else:

                response = await post_request(f'{base_url}/menus/{menu_id}/submenus/{google_submenu_id}/dishes/', json={
                    'title': google_dish['title'],
                    'description': google_dish['description'],
                    'price': google_dish['price'],
                })

                data = await response.json()

                try:
                    google_dish_id = data['id']
                except KeyError:
                    pass

                await update_sheet_values('C', google_dish['index'], google_dish_id)

            google_dishes_ids.append(google_dish_id)

            discounts[google_dish_id] = google_dish['discount']

        google_submenus_ids.append(google_submenu_id)

    for submenu_id in submenus_ids:
        if submenu_id not in google_submenus_ids:
            await delete_request(f'{base_url}/menus/{menu_id}/submenus/{submenu_id}')


async def update_db_online() -> None:
    global spreadsheet_id
    global sheet

    creds = service_account.Credentials.from_service_account_file(
        'admin/credentials.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    spreadsheet_id = '1SIh2PuXDalz2LGBWNj1bFmEMjDgbkcD-La6P20_guQI'

    r = redis.get_redis_client()

    sheet_url = 'https://docs.google.com/spreadsheets/d/1SIh2PuXDalz2LGBWNj1bFmEMjDgbkcD-La6P20_guQI/export?gid=1700880523&format=xlsx'

    df = pd.read_excel(sheet_url, header=None).fillna('')

    all_data = [list(row[:7]) for index, row in df.iterrows()]

    res = []

    ''' Парсим google_sheet '''
    for index, row in enumerate(all_data):
        if row[0]:
            res.append(
                {
                    'id': row[0],
                    'index': index,
                    'title': row[1],
                    'description': row[2],
                    'submenus': []
                }
            )

        elif row[1]:
            res[-1]['submenus'].append(
                {
                    'id': row[1],
                    'index': index,
                    'title': row[2],
                    'description': row[3],
                    'dishes': []
                }
            )

        elif row[2]:

            try:
                discount = row[6] or 0
            except IndexError:
                discount = 0

            res[-1]['submenus'][-1]['dishes'].append(
                {
                    'id': row[2],
                    'index': index,
                    'title': row[3],
                    'description': row[4],
                    'price': str(row[5]),
                    'discount': discount,
                }
            )

    global base_url
    global dishes_ids
    global discounts
    global menus_ids
    global google_dishes_ids
    global google_menus_ids

    '''
    local: 127.0.0.1:8000
    docker: app:8000
    '''

    base_url = 'http://app:8000/api/v1'

    dishes_ids = []
    menus_ids = []
    google_dishes_ids = []
    google_menus_ids = []

    discounts = {}

    tasks = []

    dishes = await fetch(f'{base_url}/menus/menu_id/submenus/google_submenu_id/dishes/')
    dishes_ids = [dish['id'] for dish in dishes] or []

    menus = await fetch(f'{base_url}/menus/')
    menus_ids = [menu['id'] for menu in menus] or []

    for google_menu in res:
        menu_id = google_menu['id']
        google_menus_ids.append(menu_id)

        task = asyncio.create_task(update_menu(menu_id, google_menu))
        tasks.append(task)

    for task in tasks:
        await task

    for dish_id in dishes_ids:
        if dish_id not in google_dishes_ids:
            await delete_request(f'{base_url}/menus/menu_id/submenus/submenu_id/dishes/{dish_id}')

    for menu_id in menus_ids:
        if menu_id not in google_menus_ids:
            await delete_request(f'{base_url}/menus/{menu_id}')

    r.set('discounts', json.dumps(jsonable_encoder(discounts)))
