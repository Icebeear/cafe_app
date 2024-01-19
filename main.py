from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.dish.router import router as dish_router
from src.menu.router import router as menu_router
from src.submenu.router import router as submenu_router

app = FastAPI(
    title="Cafe API",
    description="Home work #1 for Y_lab",
    version="0.0.1",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


api_prefix = settings.api_v1_prefix

app.include_router(router=menu_router, prefix=api_prefix)
app.include_router(router=submenu_router, prefix=api_prefix)
app.include_router(router=dish_router, prefix=api_prefix)
