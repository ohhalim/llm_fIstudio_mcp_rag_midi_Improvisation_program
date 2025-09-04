# 기본모델 클래스
from pydantic import BaseModel, EmailStr
# 타입 힌트에서 선택적 필드를 표시
from typing import Optional
# 날짜 시간타입
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    ageL Optional[int] = None
    is_active: bool =True

# 사용자 생성시 사용되는 스키마 
# UserBase를 상속받아 모든필드포함
# 추가 필드없이 그대로 사용
class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] =None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    is_active: Optional[bool] =None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datatime] = None

    class Config:
        from_attributes = True

# 이 스키마들은 fastapi에서 crud작업을 수행할때 요청응답데이터의 구조를 정의하고 검증하는 역할
