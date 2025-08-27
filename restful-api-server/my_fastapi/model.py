from ptdantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str 
    email: str 

class UserCreate(UserBase):
    password: str 

class User(UserBase):
    id: int 
    is_active: bool = True

    class Config:
        orm_mode =True

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase)
    psss

class Item(ItemBase):
    id: int
    owner_id: int
    
