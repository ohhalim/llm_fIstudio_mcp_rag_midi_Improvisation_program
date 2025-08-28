from pydantic import BaseModel, EmailStr
from typing import Optional

# 사용자 모델들
class UserBase(BaseModel):
    """사용자 기본 정보"""
    name: str
    email: EmailStr

class UserCreate(UserBase):
    """사용자 생성용 모델 (비밀번호 포함)"""
    password: str

class User(UserBase):
    """사용자 응답용 모델"""
    id: int
    is_active: bool = True

    class Config:   
        # SQLAlchemy ORM과 호환되도록 설정
        from_attributes = True

# 아이템 모델들  
class ItemBase(BaseModel):
    """아이템 기본 정보"""
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    """아이템 생성용 모델"""
    pass

class Item(ItemBase):
    """아이템 응답용 모델"""
    id: int
    owner_id: int

    class Config:
        from_attributes = True
