from sqlalchemy import String, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.settings.base import Base


class Menu(Base):
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    submenus: Mapped[list["SubMenu"]] = relationship("SubMenu", cascade="all, delete-orphan")
    submenus_count: Mapped[int] = mapped_column(Integer, default=0)
    dishes_count: Mapped[int] = mapped_column(Integer, default=0)


class SubMenu(Base):
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id", ondelete="CASCADE"))
    dishes_count: Mapped[int] = mapped_column(Integer, default=0)


class Dish(Base):
    __tablename__ = "dishes"

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    submenu_id: Mapped[int] = mapped_column(ForeignKey("submenus.id", ondelete="CASCADE"))

