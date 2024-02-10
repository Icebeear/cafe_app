from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base import Base


class Menu(Base):
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    submenus: Mapped[list['SubMenu']] = relationship(
        'SubMenu', cascade='all, delete-orphan',
        back_populates='menu'
    )


class SubMenu(Base):
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    menu_id: Mapped[int] = mapped_column(ForeignKey('menu.id', ondelete='CASCADE'))
    menu = relationship('Menu', back_populates='submenus')
    dishes: Mapped[list['Dish']] = relationship('Dish', back_populates='submenu', cascade='all, delete-orphan')


class Dish(Base):
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[str] = mapped_column(String)
    submenu_id: Mapped[int] = mapped_column(
        ForeignKey('submenu.id', ondelete='CASCADE')
    )
    submenu = relationship('SubMenu', back_populates='dishes')
