from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class SubMenuBase(BaseModel):
    title: str
    description: Annotated[str | None, Field(default=None, max_length=512)]


class SubMenuCreate(SubMenuBase):
    pass


class SubMenuRead(SubMenuBase):
    id: UUID
    dishes_count: int | None = 0


class SubMenuUpdatePartial(BaseModel):
    title: str | None = None
    description: Annotated[str | None, Field(default=None, max_length=512)]
