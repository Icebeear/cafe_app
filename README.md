# Cafe app

Cafe app - это простой HTTP сервис для ресторана / кафе.

### Инструменты

- Python >= 3.9
- FastAPI
- SQLAlchemy
- Alembic
- Asyncpg
- Uvicorn
- PostgreSQL
- Docker
- Redis
- Celery
- RabbitMQ

## Running Local
#### 1) Клонировать репозиторий

    git clone https://github.com/Icebeear/cafe_app.git


#### 2) Создать .env файл и установить переменные окружения

    DB_HOST=
    DB_PORT=
    DB_NAME=
    DB_USER=
    DB_PASS=


#### 3) Создать виртуальное окружение и установить зависимости

    python3 -m venv .venv
    .\venv\Scripts\activate (windows)
    source .venv/bin/activate (linux / macos)
    python -m pip install --upgrade pip
    pip install -r requirements.txt


#### 4) Выполнить миграции
    alembic upgrade head


#### 5) Запустить проект
    uvicorn main:app --reload


#### 6) Перейти по адресу
    http://127.0.0.1:8000/docs


## Running Dev
    docker-compose --env-file .env.dev up -d

#### Запуск проекта
    docker-compose --env-file .env.dev up -d app db redis

#### Запуск тестов
    docker-compose --env-file .env.dev up -d test-db tests

#### Документация находится по пути:
    http://localhost:8000/docs

#### Новый ORM запрос для получения количества подменю и блюд находится по пути
    src/menu/services.py

    Название метода: get_submenus_dishes

#### Аналог reverse() из django находится по пути
    tests/utils.py

    использовал в test_menu.py

#### Таска для Celery находится по пути
    tasks/tasks.py

#### ORM запрос для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами находится по пути
    src/menu/services.py

    Название метода: load_all_menus_nested

#### Функция для расчета скидки находится по пути
    src/dish/services.py

    Название метода: get_new_dish_price
