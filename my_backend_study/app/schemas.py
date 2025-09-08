from pydantic import BaseModel
from datetime import datetime

# User 생성 요청
class UserCreate(BaseModel):
    name: str
    email: str
    age: int = None

# User 응답
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
    name: str = None
    email: str = None
    age: int = None