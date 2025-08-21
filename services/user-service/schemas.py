from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# 사용자 기본 스키마
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_instruments: Optional[List[str]] = None
    music_style_preferences: Optional[List[str]] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_instruments: Optional[List[str]] = None
    music_style_preferences: Optional[List[str]] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# 인증 스키마
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

# 응답 스키마
class UserResponse(BaseModel):
    user: User
    message: str = "Success"

class UsersListResponse(BaseModel):
    users: List[User]
    total: int
    page: int
    size: int

class MessageResponse(BaseModel):
    message: str