from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, validator


class DishBase(BaseModel):
    title: str
    description: Annotated[str | None, Field(default=None, max_length=256)]
    price: Annotated[str | None, Field(default=0)]

    @validator("price")
    def check_price_format(cls, value):
        return str(round(float(value), 2))


class DishCreate(DishBase):
    pass


class DishRead(DishBase):
    id: UUID


class DishUpdatePartial(DishCreate):
    title: str | None = None
    description: Annotated[str | None, Field(default=None, max_length=256)]
    price: Annotated[str | None, Field(default=0)]
