from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.menu.router import router as menu_router
from src.settings.config import settings


app = FastAPI(
    title="Cafe API",
    description="Home work #1 for Y_lab",
    version="0.0.1",
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_allow_origins,
#     allow_credentials=settings.cors_allow_credentials,
#     allow_methods=settings.cors_allow_methods,
#     allow_headers=settings.cors_allow_headers,
# )


api_prefix = settings.api_v1_prefix

app.include_router(router=menu_router, prefix=api_prefix)
