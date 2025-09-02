from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 공통 필드
class UserBase(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_active: bool = True

# 생성 시 사용하는 스키마
class UserCreate(UserBase):
    pass

# 업데이트 시 사용하는 스키마
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None

# 응답 시 사용하는 스키마
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # SQLAlchemy 모델에서 Pydantic 모델로 변환
