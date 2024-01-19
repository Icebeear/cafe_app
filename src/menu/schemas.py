from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    title: str
    description: Annotated[str | None, Field(default=None, max_length=1024)]


class MenuCreate(MenuBase):
    pass


class MenuRead(MenuBase):
    id: UUID
    submenus_count: int | None = 0
    dishes_count: int | None = 0


class MenuUpdatePartial(MenuCreate):
    title: str | None = None
    description: Annotated[str | None, Field(default=None, max_length=1024)]