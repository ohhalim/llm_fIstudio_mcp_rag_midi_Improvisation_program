"""
사용자 관련 Pydantic 스키마
API 요청/응답 데이터의 구조와 유효성 검사를 정의합니다.
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """
    사용자의 기본 정보 스키마
    공통으로 사용되는 필드들을 정의합니다.
    """
    email: EmailStr  # 이메일 형식 자동 검증
    username: str

class UserCreate(UserBase):
    """
    사용자 생성(회원가입) 요청 스키마
    클라이언트에서 회원가입할 때 보내는 데이터 구조
    """
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        """
        비밀번호 유효성 검사
        - 최소 8자 이상
        - 영문, 숫자, 특수문자 포함 검사 가능
        """
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다.')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """
        사용자명 유효성 검사
        - 최소 3자 이상
        - 특수문자 제한 등
        """
        if len(v) < 3:
            raise ValueError('사용자명은 최소 3자 이상이어야 합니다.')
        return v

class UserLogin(BaseModel):
    """
    로그인 요청 스키마
    이메일과 비밀번호로 로그인
    """
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """
    사용자 정보 응답 스키마
    API에서 사용자 정보를 반환할 때 사용
    비밀번호는 절대 포함하지 않음!
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        # SQLAlchemy 모델을 Pydantic 모델로 자동 변환 허용
        from_attributes = True

class UserUpdate(BaseModel):
    """
    사용자 정보 수정 스키마
    수정 가능한 필드들만 포함, 모든 필드는 선택사항
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError('사용자명은 최소 3자 이상이어야 합니다.')
        return v

class Token(BaseModel):
    """
    JWT 토큰 응답 스키마
    로그인 성공 시 반환되는 토큰 정보
    """
    access_token: str
    token_type: str = "bearer"  # 기본값으로 "bearer" 설정

class TokenData(BaseModel):
    """
    JWT 토큰에서 추출한 데이터 스키마
    토큰 검증 시 사용
    """
    email: Optional[str] = None