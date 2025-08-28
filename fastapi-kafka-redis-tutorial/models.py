"""
models.py - 데이터 모델 정의

이 파일에서 배울 수 있는 개념들:
1. Pydantic 모델: 데이터 검증과 직렬화/역직렬화
2. 상속을 통한 코드 재사용
3. 선택적 필드 (Optional)
4. 기본값 설정
5. 모델 구성 (Config)
6. 타입 힌팅
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enum 클래스 - 상수 정의에 유용
class UserStatus(str, Enum):
    """
    사용자 상태를 나타내는 열거형
    
    str을 상속받아 JSON 직렬화가 쉽게 됩니다.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    PENDING = "pending"


class EventType(str, Enum):
    """
    이벤트 타입을 나타내는 열거형
    """
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"


# 기본 모델 클래스들
class UserBase(BaseModel):
    """
    사용자 기본 정보를 담는 베이스 모델
    
    다른 사용자 모델들이 이 클래스를 상속받아 공통 필드를 재사용합니다.
    상속을 통해 코드 중복을 줄이고 일관성을 유지할 수 있습니다.
    """
    name: str = Field(..., min_length=1, max_length=100, description="사용자 이름")
    email: EmailStr = Field(..., description="이메일 주소")
    age: Optional[int] = Field(None, ge=0, le=150, description="나이 (0-150)")
    phone: Optional[str] = Field(None, regex=r"^\d{10,11}$", description="전화번호")
    
    # 커스텀 검증자 (validator)
    @validator('name')
    def validate_name(cls, v):
        """
        이름 필드의 커스텀 검증
        
        @validator 데코레이터를 사용하여 필드별 검증 로직을 추가할 수 있습니다.
        """
        if not v.strip():  # 공백만 있는 경우
            raise ValueError('이름은 공백만으로 구성될 수 없습니다')
        return v.strip().title()  # 앞글자만 대문자로 변환
    
    @validator('email')
    def validate_email(cls, v):
        """
        이메일 필드의 커스텀 검증
        """
        # EmailStr 타입이 기본 검증을 해주지만, 추가 검증을 원할 때 사용
        if 'test' in str(v).lower() and 'example' not in str(v).lower():
            # 개발용 테스트 이메일은 허용하지만 실제 test 이메일은 제한
            pass
        return v


class UserCreate(UserBase):
    """
    사용자 생성 시 사용되는 모델
    
    UserBase의 모든 필드를 상속받고, 추가로 비밀번호 필드를 가집니다.
    """
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)")
    
    @validator('password')
    def validate_password(cls, v):
        """
        비밀번호 강도 검증
        """
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')
        
        # 숫자, 영문자 포함 검사
        has_digit = any(c.isdigit() for c in v)
        has_alpha = any(c.isalpha() for c in v)
        
        if not (has_digit and has_alpha):
            raise ValueError('비밀번호는 숫자와 영문자를 모두 포함해야 합니다')
        
        return v


class UserUpdate(BaseModel):
    """
    사용자 정보 수정 시 사용되는 모델
    
    모든 필드가 Optional입니다. 변경하고 싶은 필드만 전달하면 됩니다.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    phone: Optional[str] = Field(None, regex=r"^\d{10,11}$")
    status: Optional[UserStatus] = None


class User(UserBase):
    """
    실제 사용자 정보를 나타내는 모델 (응답용)
    
    데이터베이스에서 조회된 사용자 정보를 API 응답으로 보낼 때 사용합니다.
    비밀번호 같은 민감한 정보는 포함하지 않습니다.
    """
    id: int = Field(..., description="사용자 고유 ID")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="사용자 상태")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: Optional[datetime] = Field(None, description="수정 시간")
    login_count: int = Field(default=0, description="로그인 횟수")
    
    class Config:
        """
        Pydantic 모델 설정
        """
        # ORM 모드: SQLAlchemy 같은 ORM 객체를 Pydantic 모델로 변환할 때 사용
        orm_mode = True
        
        # JSON 스키마에서 예시 데이터
        schema_extra = {
            "example": {
                "id": 1,
                "name": "홍길동",
                "email": "hong@example.com",
                "age": 25,
                "phone": "01012345678",
                "status": "active",
                "created_at": "2024-01-01T00:00:00",
                "login_count": 5
            }
        }


# 아이템 관련 모델들
class ItemBase(BaseModel):
    """
    아이템 기본 정보 모델
    """
    title: str = Field(..., min_length=1, max_length=200, description="제목")
    description: Optional[str] = Field(None, max_length=1000, description="설명")
    price: Optional[float] = Field(None, ge=0, description="가격")
    category: Optional[str] = Field(None, max_length=50, description="카테고리")


class ItemCreate(ItemBase):
    """
    아이템 생성용 모델
    """
    pass  # ItemBase와 동일하므로 별도 필드 추가 없음


class Item(ItemBase):
    """
    아이템 정보 모델 (응답용)
    """
    id: int = Field(..., description="아이템 고유 ID")
    owner_id: int = Field(..., description="소유자 ID")
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True, description="활성 상태")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "맛있는 사과",
                "description": "신선한 사과입니다",
                "price": 1000.0,
                "category": "과일",
                "owner_id": 1,
                "created_at": "2024-01-01T00:00:00",
                "is_active": True
            }
        }


# 이벤트 관련 모델들
class EventBase(BaseModel):
    """
    이벤트 기본 모델
    
    Kafka 메시지로 전송될 이벤트 데이터를 정의합니다.
    """
    event_type: EventType = Field(..., description="이벤트 타입")
    user_id: Optional[int] = Field(None, description="관련 사용자 ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="이벤트 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="이벤트 발생 시간")


class KafkaMessage(BaseModel):
    """
    Kafka 메시지 모델
    """
    topic: str = Field(..., description="토픽 이름")
    key: Optional[str] = Field(None, description="메시지 키")
    value: Dict[str, Any] = Field(..., description="메시지 내용")
    headers: Optional[Dict[str, str]] = Field(None, description="메시지 헤더")


# API 응답 모델들
class APIResponse(BaseModel):
    """
    표준 API 응답 모델
    
    모든 API 응답에 일관된 형태를 제공합니다.
    """
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[Any] = Field(None, description="응답 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")


class PaginatedResponse(BaseModel):
    """
    페이지네이션 응답 모델
    
    대량의 데이터를 페이지 단위로 나누어 응답할 때 사용합니다.
    """
    items: List[Any] = Field(..., description="아이템 목록")
    total: int = Field(..., description="전체 아이템 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")
    
    @validator('pages', always=True)
    def calculate_pages(cls, v, values):
        """
        전체 페이지 수 자동 계산
        """
        total = values.get('total', 0)
        size = values.get('size', 1)
        return (total + size - 1) // size if size > 0 else 0


# 통계 관련 모델
class UserStats(BaseModel):
    """
    사용자 통계 모델
    """
    total_users: int = Field(..., description="전체 사용자 수")
    active_users: int = Field(..., description="활성 사용자 수")
    new_users_today: int = Field(..., description="오늘 가입한 사용자 수")
    login_count_today: int = Field(..., description="오늘 로그인 수")


# 헬스체크 모델
class HealthCheck(BaseModel):
    """
    시스템 상태 확인 모델
    """
    status: str = Field(..., description="시스템 상태")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(default_factory=dict, description="각 서비스 상태")
    version: str = Field(..., description="애플리케이션 버전")


if __name__ == "__main__":
    """
    모델 테스트 코드
    이 파일을 직접 실행하면 모델들의 동작을 확인할 수 있습니다.
    """
    
    # User 모델 테스트
    user_data = {
        "name": "홍길동",
        "email": "hong@example.com",
        "age": 25,
        "phone": "01012345678"
    }
    
    user = User(id=1, **user_data)
    print("생성된 사용자:")
    print(user.json(indent=2, ensure_ascii=False))
    
    # 이벤트 모델 테스트
    event = EventBase(
        event_type=EventType.USER_CREATED,
        user_id=1,
        data={"email": "hong@example.com"}
    )
    print("\n생성된 이벤트:")
    print(event.json(indent=2, ensure_ascii=False))