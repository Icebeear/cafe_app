from typing import Annotated

from pydantic import UUID4, BaseModel, Field


class SubMenuBase(BaseModel):
    title: str
    description: Annotated[str | None, Field(default=None, max_length=512)]


class SubMenuCreate(SubMenuBase):
    pass


class SubMenuRead(SubMenuBase):
    id: UUID4
    dishes_count: int | None = 0


class SubMenuUpdatePartial(BaseModel):
    title: str | None = None
    description: Annotated[str | None, Field(default=None, max_length=512)]
