# Cafe app

Cafe app - это простой HTTP сервис для ресторана / кафе.

### Инструменты

- Python >= 3.9
- FastAPI
- SQLAlchemy
- Alembic 
- Asyncpg 
- Uvicorn 

## Running Local
#### 1) Клонировать репозиторий 

    git clone https://github.com/Icebeear/cafe_app.git


#### 2) Создать .env файл и установить переменные окружения

    DB_HOST=
    DB_PORT=
    DB_NAME=
    DB_USER=
    DB_PASS=

    DB_HOST=db
    DB_PORT=5432
    DB_NAME=postgres
    DB_USER=postgres
    DB_PASS=postgres

    DB_HOST_TEST=test-db
    DB_PORT_TEST=8080
    DB_NAME_TEST=postgres-test
    DB_USER_TEST=postgres-test
    DB_PASS_TEST=postgres-test


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

#### Документация находится по пути:
    http://localhost:8000/docs

#### Новый ORM запрос для получения количества подменю и блюд находится по пути 
    src/menu/utils.py 
    
    Название метода: get_submenus_dishes
    