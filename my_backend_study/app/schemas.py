from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User 생성 요청 / 요청 데이터 검증
class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

# User 응답 / 응답 데이터 형식
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# User 업데이트 요청
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None