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
    docker-compose up -d
    