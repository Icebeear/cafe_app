from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

'''Menu schemas'''
class MenuBase(BaseModel):
    title: str 
    description: Annotated[str | None, Field(default=None, max_length=1024)] 


class MenuCreate(MenuBase):
    pass 


class MenuRead(MenuBase):
    id: UUID

    # model_config = ConfigDict(coerce_numbers_to_str=True)  

    
class MenuUpdatePartial(MenuCreate):
    title: str | None = None 
    description: Annotated[str | None, Field(default=None, max_length=1024)] 


'''SubMenu schemas'''
class SubMenuBase(BaseModel):
    title: str 
    description: Annotated[str | None, Field(default=None, max_length=512)] 


class SubMenuCreate(SubMenuBase):
    pass 


class SubMenuRead(SubMenuBase):
    id: UUID 

    model_config = ConfigDict(coerce_numbers_to_str=True)   



'''Dish schemas'''
class Dish(BaseModel):
    title: str 
    description: Annotated[str | None, Field(default=None, max_length=512)]  
    price: float 