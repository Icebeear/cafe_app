import asyncio
import json
from typing import Any

import pandas as pd
from fastapi.encoders import jsonable_encoder
from google.oauth2 import service_account
from googleapiclient.discovery import build

from src.core.config import settings
from src.core.database import get_async_context
from src.dish.crud import create_dish, delete_dish, get_dish_by_id, update_dish_partial
from src.dish.schemas import DishCreate, DishRead, DishUpdatePartial
from src.dish.services import clear_dish_cache, load_all_dishes
from src.menu.crud import (
    create_menu,
    delete_menu,
    get_menu_by_id,
    get_menu_by_title,
    update_menu_partial,
)
from src.menu.schemas import MenuCreate, MenuRead, MenuUpdatePartial
from src.menu.services import clear_menu_cache, load_all_menus
from src.redis.utils import redis
from src.submenu.crud import (
    create_submenu,
    delete_submenu,
    get_submenu_by_id,
    update_submenu_partial,
)
from src.submenu.schemas import SubMenuCreate, SubMenuRead, SubMenuUpdatePartial
from src.submenu.services import clear_submenu_cache, load_all_submenus


class DbUpdater:
    def __init__(self) -> None:
        self.redis = redis

        self.dishes_ids: list[str] = []
        self.menus_ids: list[str] = []

        self.google_dishes_ids: list[str] = []
        self.google_menus_ids: list[str] = []

        self.discounts: dict[str, float] = {}

    async def parse_google_sheet(self) -> list[dict[str, Any]]:

        creds = service_account.Credentials.from_service_account_file(
            'admin/credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

        service = build('sheets', 'v4', credentials=creds)

        self.sheet_url = settings.google_sheet_url.replace('edit#', 'export?') + '&format=xlsx'  # type: ignore
        self.spreadsheet_id = self.sheet_url.split('/')[5]
        self.sheet = service.spreadsheets()

        df = pd.read_excel(self.sheet_url, header=None).fillna('')

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

        return res

    async def update_all_data(self, menu: MenuRead, google_menu: dict[str, Any]) -> None:
        async with get_async_context() as session:
            serialized_submenus = await self.get_all_submenus(menu)

            submenus_ids = [submenu['id'] for submenu in serialized_submenus] or []
            submenus_titles = [submenu['title'] for submenu in serialized_submenus] or []

            google_submenus_ids = []

            for google_submenu in google_menu['submenus']:
                google_submenu_id = google_submenu['id']
                google_submenu_title = google_submenu['title']

                new_submenu = SubMenuUpdatePartial(
                    title=google_submenu['title'],
                    description=google_submenu['description']
                )

                if google_submenu_id in submenus_ids:

                    submenu = await get_submenu_by_id(session, google_submenu_id)

                    redis.clear_cache(
                        f'{submenu.menu_id}_submenu_{submenu.id}',
                        'all_submenus'
                    )

                    await update_submenu_partial(session, submenu, new_submenu)

                elif google_submenu_title in submenus_titles:

                    submenu_id = [submenu['id']
                                  for submenu in serialized_submenus if submenu['title'] == google_submenu_title][0]

                    submenu = await get_submenu_by_id(session, submenu_id)

                    redis.clear_cache(
                        f'{submenu.menu_id}_submenu_{submenu.id}',
                        'all_submenus'
                    )

                    await update_submenu_partial(session, submenu, new_submenu)

                    google_submenu_id = submenu_id

                else:

                    redis.clear_cache(
                        'all_menus',
                        'all_submenus',
                        f'menu_{menu.id}',
                        'all_menus_nested'
                    )

                    submenu = await create_submenu(session, menu, new_submenu)

                    google_submenu_id = str(submenu.id)

                await self.update_sheet_values('B', google_submenu['index'], str(google_submenu_id))

                for google_dish in google_submenu['dishes']:
                    google_dish_id = google_dish['id']

                    new_dish = DishUpdatePartial(
                        title=google_dish['title'],
                        description=google_dish['description'],
                        price=google_dish['price']
                    )

                    if google_dish_id in self.dishes_ids:

                        dish = await get_dish_by_id(session, google_dish_id)

                        redis.clear_cache(
                            f'{dish.submenu_id}_dish_{dish.id}',
                            'all_dishes',
                            'all_menus_nested'
                        )
                        await update_dish_partial(session, dish, new_dish)

                    else:

                        redis.clear_cache('all_dishes')
                        clear_menu_cache(menu.id)
                        clear_submenu_cache(menu.id, submenu.id)

                        dish = await create_dish(session, new_dish, submenu)

                        google_dish_id = str(dish.id)

                        await self.update_sheet_values('C', google_dish['index'], str(google_dish_id))

                    self.google_dishes_ids.append(google_dish_id)

                    self.discounts[google_dish_id] = google_dish['discount']

                google_submenus_ids.append(google_submenu_id)

            for submenu_id in submenus_ids:
                if submenu_id not in google_submenus_ids:
                    submenu = await get_submenu_by_id(session, submenu_id)
                    clear_submenu_cache(
                        submenu.menu_id,
                        submenu.id
                    )
                    await delete_submenu(session, submenu)

    async def create_all_data(self, menu: MenuRead, google_menu: dict[str, Any]) -> None:
        async with get_async_context() as session:
            await self.update_sheet_values('A', google_menu['index'], str(menu.id))

            for google_submenu in google_menu['submenus']:

                submenu_create = SubMenuCreate(
                    title=google_submenu['title'],
                    description=google_submenu['description']
                )

                redis.clear_cache(
                    'all_menus',
                    'all_submenus',
                    f'menu_{menu.id}',
                    'all_menus_nested'
                )

                submenu = await create_submenu(session, menu, submenu_create)

                await self.update_sheet_values('B', google_submenu['index'], str(submenu.id))

                for google_dish in google_submenu['dishes']:

                    dish_create = DishCreate(
                        title=google_dish['title'],
                        description=google_dish['description'],
                        price=google_dish['price']
                    )

                    redis.clear_cache('all_dishes')
                    clear_menu_cache(menu.id)
                    clear_submenu_cache(menu.id, submenu.id)

                    dish = await create_dish(session, dish_create, submenu)

                    self.google_dishes_ids.append(str(dish.id))

                    await self.update_sheet_values('C', google_dish['index'], str(dish.id))

    async def update_menu(self, menu_id: str, google_menu: dict[str, Any]) -> None:
        async with get_async_context() as session:
            '''
            Идем в бд по id меню из таблицы, если оно есть, сразу патчим
            и обновляем зависимости.
            '''
            try:
                menu = await get_menu_by_id(session, menu_id)
            except Exception:
                menu = None

            if menu:
                menu_update = MenuUpdatePartial(
                    title=google_menu['title'],
                    description=google_menu['description']
                )

                self.redis.clear_cache(
                    f'menu_{menu.id}',
                    'all_menus',
                    'all_menus_nested'
                )

                await update_menu_partial(session, menu, menu_update)

                await self.update_all_data(menu, google_menu)

            else:
                '''
                Если не нашли по id (значит меню либо нету, либо до этого когда то создавалось в бд вручную),
                проверяем нету ли с меню с таким названием, если есть - то получаем его id и обновлянем зависимости.
                Если нету, то создаем его и все зависимости.
                '''
                async with get_async_context() as session:

                    menu = await get_menu_by_title(session, google_menu['title'])

                    if menu:
                        serialized_menus = await self.get_all_menus()

                        menu_id = [menu['id'] for menu in serialized_menus if google_menu['title'] == menu['title']][0]

                        await self.update_all_data(menu, google_menu)

                    else:
                        menu_create = MenuCreate(
                            title=google_menu['title'],
                            description=google_menu['description']
                        )

                        redis.clear_cache('all_menus', 'all_menus_nested')

                        menu = await create_menu(session, menu_create)

                        self.google_menus_ids.append(str(menu.id))

                        await self.create_all_data(menu, google_menu)

    async def update_sheet_values(self, table: str, row: int, values: str) -> None:
        ''' Метод для вставки данных в таблицу google_sheet '''
        self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f'sheet1!{table}{row + 1}',
            valueInputOption='RAW',
            body={'values': [[values]]}
        ).execute()

    async def delete_conflict_objects(self) -> None:

        ''' Метод удаляет все блюды и меню которые есть в бд, но отсутсвуют в таблице '''

        async with get_async_context() as session:
            dishes: list[DishRead] = await self.get_all_dishes()
            menus: list[MenuRead] = await self.get_all_menus()

            for dish in dishes:
                dish_id = dish.get('id')
                dish_submenu_id = dish.get('submenu_id')
                if dish_id not in self.google_dishes_ids:
                    dish = await get_dish_by_id(session, dish_id)
                    clear_dish_cache(dish_submenu_id, dish_id)
                    await delete_dish(session, dish)

            for menu in menus:
                menu_id = menu.get('id')
                if menu_id not in self.google_menus_ids:
                    menu = await get_menu_by_id(session, menu_id)  # type: ignore
                    clear_menu_cache(menu_id)
                    await delete_menu(session, menu)

            self.google_menus_ids = []
            self.google_dishes_ids = []

    async def get_all_menus(self) -> list[MenuRead]:
        async with get_async_context() as session:
            all_menus = await load_all_menus(session, 0, 100)
            if all(isinstance(menu, dict) for menu in all_menus):
                serialized_menus = all_menus
            else:
                serialized_menus = []
                for menu in all_menus:
                    serialized_menus.append({  # type: ignore
                        'id': str(menu.id),
                        'title': menu.title,
                        'description': menu.description
                    })

        return serialized_menus

    async def get_all_dishes(self) -> list[DishRead]:
        async with get_async_context() as session:
            dishes = await load_all_dishes(session, 0, 100)
            if all(isinstance(dish, dict) for dish in dishes):
                serialized_dishes = dishes
            else:
                serialized_dishes = []
                for dish in dishes:
                    serialized_dishes.append({  # type: ignore
                        'id': str(dish.id),
                        'title': dish.title,
                        'description': dish.description,
                        'price': dish.price
                    })

        return serialized_dishes

    async def get_all_submenus(self, menu: MenuRead) -> list[SubMenuRead]:
        async with get_async_context() as session:
            submenus = await load_all_submenus(session, menu, 0, 100)
            if all(isinstance(submenu, dict) for submenu in submenus):
                serialized_submenus = submenus
            else:
                serialized_submenus = []
                for submenu in submenus:
                    serialized_submenus.append({  # type: ignore
                        'id': str(submenu.id),
                        'title': submenu.title,
                        'description': submenu.description
                    })

        return serialized_submenus

    async def update_db_online(self) -> None:
        dishes = await self.get_all_dishes()
        self.dishes_ids = [dish['id'] for dish in dishes]

        res = await self.parse_google_sheet()
        tasks = []

        for google_menu in res:
            menu_id = google_menu['id']
            self.google_menus_ids.append(str(menu_id))

            task = asyncio.create_task(self.update_menu(menu_id, google_menu))
            tasks.append(task)

        for task in tasks:
            await task

        await self.delete_conflict_objects()

        self.redis.get_redis_client().set('discounts', json.dumps(jsonable_encoder(self.discounts)))


db_updater = DbUpdater()
