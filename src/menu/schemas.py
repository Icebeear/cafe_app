from typing import Annotated

from pydantic import UUID4, BaseModel, Field

from src.submenu.schemas import SubMenuReadNested


class MenuBase(BaseModel):
    title: str
    description: Annotated[str | None, Field(default=None, max_length=1024)]


class MenuCreate(MenuBase):
    pass


class MenuRead(MenuBase):
    id: UUID4
    submenus_count: int | None = 0
    dishes_count: int | None = 0


class MenuUpdatePartial(BaseModel):
    title: str | None = None
    description: Annotated[str | None, Field(default=None, max_length=1024)]


class MenuReadNested(MenuBase):
    id: UUID4
    submenus: list[SubMenuReadNested] | None
