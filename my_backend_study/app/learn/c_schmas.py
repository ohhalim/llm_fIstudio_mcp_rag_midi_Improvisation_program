from pydantic import BaseModel
from datetime import datetime

class userCreate(BaseModel):
    name: str
    email: str
    age: int = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int =None
    create_at: datetime

    class Config:
        from_attributes = True

clase UserUpdate(BaseModel):
    name: str = None
    email: str None
    age: int = None