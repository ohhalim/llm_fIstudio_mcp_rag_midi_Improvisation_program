# 🎓 FastAPI + PostgreSQL + Kafka + Redis 완벽 학습 가이드

> 현대적인 마이크로서비스 아키텍처의 모든 것을 배워보는 실습 중심 가이드

---

## 📋 목차

1. [전체 아키텍처 이해](#1-전체-아키텍처-이해)
2. [핵심 개념 학습](#2-핵심-개념-학습)
3. [데이터베이스 패턴](#3-데이터베이스-패턴)
4. [서비스 레이어 분석](#4-서비스-레이어-분석)
5. [API 설계 패턴](#5-api-설계-패턴)
6. [캐시 전략](#6-캐시-전략)
7. [이벤트 기반 아키텍처](#7-이벤트-기반-아키텍처)
8. [실습 과제](#8-실습-과제)
9. [문제 해결](#9-문제-해결)

---

## 1. 전체 아키텍처 이해

### 🏗️ 시스템 구성도
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   PostgreSQL    │    │     Redis       │
│   Web Server    │◄──►│    Database     │◄──►│     Cache       │
│                 │    │                 │    │                 │
│ • REST API      │    │ • 사용자 데이터 │    │ • 사용자 캐시   │
│ • JWT 인증      │    │ • 관계형 스키마 │    │ • 세션 저장     │
│ • 비즈니스로직  │    │ • ACID 트랜잭션 │    │ • 통계 데이터   │
│ • 데이터 검증   │    │ • 인덱스 최적화 │    │ • 임시 데이터   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │        Kafka            │
                    │    Event Stream         │
                    │                         │
                    │ • 이벤트 발행           │
                    │ • 비동기 처리           │
                    │ • 메시지 큐             │
                    └─────────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Kafka Consumer         │
                    │                           │
                    │ • 이벤트 처리             │
                    │ • 후속 작업 실행          │
                    │ • 로그 기록               │
                    └───────────────────────────┘
```

### 🔄 데이터 흐름 과정
1. **사용자 요청** → FastAPI (API Gateway)
2. **인증 처리** → JWT 토큰 검증
3. **비즈니스 로직** → 서비스 레이어에서 처리
4. **데이터 저장** → PostgreSQL (영구 저장)
5. **캐시 저장** → Redis (빠른 조회)
6. **이벤트 발행** → Kafka (비동기 처리)
7. **후속 처리** → Consumer (이메일, 알림 등)

---

## 2. 핵심 개념 학습

### 🎯 FastAPI 핵심 개념

#### 📁 `main.py` - 애플리케이션 진입점
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Tutorial API",
    description="FastAPI + PostgreSQL + Kafka + Redis",
    version="1.0.0"
)

# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])
```

**학습 포인트:**
- **미들웨어**: 요청/응답 전처리
- **라우터 분리**: 모듈화된 API 설계
- **자동 문서화**: Swagger UI 자동 생성

#### 📁 `config.py` - 설정 관리
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 데이터베이스 설정
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/db"
    database_sync_url: str = "postgresql://user:pass@localhost:5432/db"
    
    # JWT 설정
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Redis 설정
    redis_url: str = "redis://localhost:6379"
    
    # Kafka 설정
    kafka_bootstrap_servers: str = "localhost:9092"
    
    class Config:
        env_file = ".env"  # 환경변수 파일에서 자동 로드

settings = Settings()
```

**학습 포인트:**
- **환경별 설정**: 개발/운영 환경 분리
- **타입 검증**: Pydantic 자동 검증
- **보안**: 민감 정보 환경변수 관리

---

## 3. 데이터베이스 패턴

### 🐘 PostgreSQL + SQLAlchemy 2.0

#### 📁 `database.py` - 비동기 연결 관리
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

# 비동기 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=True,  # SQL 로그 출력
    pool_size=20,  # 연결 풀 크기
    max_overflow=0,
    pool_pre_ping=True,  # 연결 상태 확인
)

# 세션 팩토리
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_async_session():
    """비동기 데이터베이스 세션 컨텍스트 매니저"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # 자동 커밋
        except Exception:
            await session.rollback()  # 오류 시 롤백
            raise
        finally:
            await session.close()
```

**학습 포인트:**
- **비동기 ORM**: async/await 패턴 사용
- **연결 풀링**: 효율적인 DB 연결 관리
- **트랜잭션**: 자동 커밋/롤백 처리

#### 📁 `db_models.py` - ORM 모델 정의
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import datetime

Base = declarative_base()

class TimestampMixin:
    """공통 타임스탬프 필드"""
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, 
                       onupdate=datetime.datetime.utcnow, nullable=False)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer)
    phone = Column(String(20))
    status = Column(String(20), nullable=False, default="active")
    login_count = Column(Integer, default=0)
    
    # 관계 설정
    activities = relationship("UserActivity", back_populates="user", 
                            cascade="all, delete-orphan")

class UserActivity(Base, TimestampMixin):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String(100), nullable=False)
    description = Column(Text)
    data = Column(JSONB)  # PostgreSQL JSONB 타입
    
    # 관계 설정
    user = relationship("User", back_populates="activities")
```

**학습 포인트:**
- **Mixin 패턴**: 공통 필드 재사용
- **관계 매핑**: Foreign Key와 relationship
- **인덱싱**: 쿼리 성능 최적화
- **JSONB**: 유연한 데이터 저장

### 🔄 마이그레이션 관리

#### 📁 `migrations/versions/001_initial_migration.py`
```python
def upgrade() -> None:
    """데이터베이스 스키마 업그레이드"""
    # users 테이블 생성
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    
    # 인덱스 생성
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade() -> None:
    """데이터베이스 스키마 다운그레이드"""
    op.drop_table('users')
```

**학습 포인트:**
- **스키마 버전 관리**: Git처럼 DB 변경 추적
- **업그레이드/다운그레이드**: 양방향 마이그레이션
- **팀 협업**: 스키마 변경 충돌 방지

---

## 4. 서비스 레이어 분석

### 👤 사용자 서비스 (`services/user_service.py`)

이 파일이 **가장 중요한 학습 대상**입니다! 모든 패턴이 집약되어 있어요.

#### 🔐 사용자 생성 과정
```python
async def create_user(self, user_data: UserCreate) -> Optional[User]:
    """사용자 생성 - 전체 워크플로우 예시"""
    async with get_async_session() as session:
        try:
            # 1️⃣ 비즈니스 규칙 검증
            existing_user = await self._find_user_by_email(session, user_data.email)
            if existing_user:
                logger.warning(f"⚠️ 이메일 중복: {user_data.email}")
                return None
            
            # 2️⃣ 보안 처리 (bcrypt 해싱)
            hashed_password = self.auth.hash_password(user_data.password)
            
            # 3️⃣ 데이터베이스 저장
            db_user = DBUser(
                name=user_data.name,
                email=user_data.email,
                password_hash=hashed_password,
                age=user_data.age,
                phone=user_data.phone,
                status=UserStatus.ACTIVE,
                login_count=0
            )
            
            session.add(db_user)
            await session.flush()  # ID 생성을 위해 flush
            await session.refresh(db_user)  # 최신 데이터 가져오기
            
            # 4️⃣ Pydantic 모델로 변환
            new_user = User(
                id=db_user.id,
                name=db_user.name,
                email=db_user.email,
                # ... 기타 필드들
            )
            
            # 5️⃣ 캐시 저장 (Cache-Aside 패턴)
            await self.redis.set_user_cache(
                db_user.id, 
                new_user.dict(), 
                expire=3600
            )
            
            # 6️⃣ 활동 로그 기록
            await self._log_user_activity(
                session=session,
                user_id=db_user.id,
                activity_type="user_created",
                description="새 사용자 계정 생성"
            )
            
            # 7️⃣ 이벤트 발행 (비동기 처리)
            await publish_user_event(
                event_type=EventType.USER_CREATED,
                user_id=db_user.id,
                data={
                    "email": new_user.email,
                    "name": new_user.name
                }
            )
            
            return new_user
            
        except Exception as e:
            logger.error(f"❌ 사용자 생성 중 오류: {e}")
            return None
```

**이 코드에서 배우는 핵심 패턴들:**

1. **트랜잭션 관리** 🔒
   - `async with get_async_session()`: 자동 커밋/롤백
   - `flush()` vs `commit()`: ID 생성 타이밍

2. **에러 처리** ⚠️
   - try-except로 안전한 처리
   - 로깅을 통한 디버깅

3. **보안** 🛡️
   - 비밀번호 해싱 (bcrypt)
   - 입력 데이터 검증

4. **성능 최적화** ⚡
   - 캐시 저장 (빠른 조회)
   - 비동기 이벤트 처리

#### 🎯 Cache-Aside 패턴 구현
```python
async def get_user(self, user_id: int) -> Optional[User]:
    """Cache-Aside 패턴의 완벽한 예시"""
    try:
        # 1️⃣ 캐시에서 먼저 조회 (빠름)
        cached_user = await self.redis.get_user_cache(user_id)
        if cached_user:
            logger.info(f"🎯 캐시 히트: 사용자 {user_id}")
            return User(**cached_user)
        
        # 2️⃣ 캐시 미스 - PostgreSQL에서 조회
        logger.info(f"🔍 캐시 미스: 사용자 {user_id} - DB 조회")
        
        async with get_async_session() as session:
            stmt = select(DBUser).where(DBUser.id == user_id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                return None
            
            # 3️⃣ Pydantic 모델로 변환
            user = User(
                id=db_user.id,
                name=db_user.name,
                email=db_user.email,
                # ... 기타 필드들
            )
            
            # 4️⃣ 캐시에 저장 (다음 번 조회 시 빠름)
            await self.redis.set_user_cache(user_id, user.dict(), expire=3600)
            
            return user
        
    except Exception as e:
        logger.error(f"❌ 사용자 조회 중 오류: {e}")
        return None
```

**Cache-Aside 패턴의 장점:**
- **성능**: 캐시 히트 시 매우 빠른 응답
- **일관성**: 애플리케이션이 캐시를 직접 관리
- **유연성**: 캐시 전략을 세밀하게 제어

### 🔐 인증 서비스 (`services/auth_service.py`)

```python
class AuthService:
    def hash_password(self, password: str) -> str:
        """bcrypt를 이용한 안전한 비밀번호 해싱"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            hashed.encode('utf-8')
        )
    
    def create_access_token(self, data: dict) -> str:
        """JWT 액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
```

**학습 포인트:**
- **bcrypt**: 솔트 + 해싱으로 레인보우 테이블 공격 방어
- **JWT**: Stateless 인증, 확장성 좋음
- **만료 시간**: 보안을 위한 토큰 수명 관리

---

## 5. API 설계 패턴

### 📡 사용자 API (`routers/users.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/users/", response_model=User)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """사용자 생성 API"""
    user = await user_service.create_user(user_data)
    if not user:
        raise HTTPException(
            status_code=400, 
            detail="이미 존재하는 이메일입니다"
        )
    return user

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """사용자 조회 API"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user

@router.get("/users/", response_model=List[User])
async def list_users(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[UserStatus] = None
):
    """사용자 목록 조회 (페이징 + 필터링)"""
    return await user_service.list_users(skip, limit, status)
```

**REST API 설계 원칙:**
- **명사형 URL**: `/users/` (동사 아님)
- **HTTP 메서드**: GET(조회), POST(생성), PUT(수정), DELETE(삭제)
- **상태 코드**: 200(성공), 400(잘못된 요청), 404(없음)
- **응답 모델**: Pydantic으로 자동 검증 및 문서화

### 📊 데이터 모델 (`models.py`)

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    """사용자 기본 정보"""
    name: str
    email: EmailStr  # 자동 이메일 검증
    age: Optional[int] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    """사용자 생성용 모델"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상이어야 합니다')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('나이는 0-150 사이여야 합니다')
        return v

class User(UserBase):
    """사용자 응답용 모델 (비밀번호 제외)"""
    id: int
    status: UserStatus
    login_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # SQLAlchemy 모델과 호환
```

**Pydantic의 강력한 기능:**
- **자동 검증**: 타입, 이메일 형식 등 자동 체크
- **커스텀 검증**: `@validator`로 비즈니스 룰 적용
- **JSON 직렬화**: 자동 JSON 변환
- **문서 자동 생성**: OpenAPI 스키마 생성

---

## 6. 캐시 전략

### 🔴 Redis 서비스 (`services/redis_service.py`)

```python
class RedisService:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
    
    async def set_user_cache(self, user_id: int, user_data: dict, expire: int = 3600):
        """사용자 캐시 저장"""
        key = f"user:{user_id}"
        try:
            await self.redis.setex(
                key, 
                expire, 
                json.dumps(user_data, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Redis 저장 실패: {e}")
            return False
    
    async def get_user_cache(self, user_id: int) -> Optional[dict]:
        """사용자 캐시 조회"""
        key = f"user:{user_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis 조회 실패: {e}")
            return None
    
    async def delete_user_cache(self, user_id: int):
        """사용자 캐시 삭제"""
        key = f"user:{user_id}"
        return await self.redis.delete(key)
```

### 🎯 캐시 전략 패턴들

#### 1. **Cache-Aside (Lazy Loading)**
```python
# 1. 캐시 먼저 확인
data = await redis.get(key)
if data:
    return data  # 캐시 히트

# 2. 캐시 미스 - DB 조회
data = await db.query(...)
if data:
    # 3. 캐시에 저장
    await redis.set(key, data, expire=3600)
    
return data
```

**장점:** 필요한 데이터만 캐시에 저장
**단점:** 첫 번째 조회는 느림

#### 2. **Write-Through**
```python
# 데이터 쓰기 시 DB와 캐시 동시 업데이트
async def update_user(user_id, data):
    # 1. DB 업데이트
    await db.update(user_id, data)
    
    # 2. 캐시 업데이트
    await redis.set(f"user:{user_id}", data)
```

**장점:** 데이터 일관성 보장
**단점:** 쓰기 성능 영향

#### 3. **Write-Behind (Write-Back)**
```python
# 캐시만 먼저 업데이트, DB는 나중에 배치 처리
async def update_user_cache_only(user_id, data):
    await redis.set(f"user:{user_id}", data)
    await redis.lpush("dirty_users", user_id)  # 나중에 DB 업데이트 대상
```

**장점:** 빠른 쓰기 성능
**단점:** 데이터 손실 위험

---

## 7. 이벤트 기반 아키텍처

### ⚡ Kafka 프로듀서 (`services/kafka_service.py`)

```python
class KafkaService:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
    
    async def send_event(self, topic: str, event_data: dict) -> bool:
        """이벤트 발행"""
        try:
            await self.producer.send(topic, event_data)
            logger.info(f"✅ 이벤트 발행: {topic}")
            return True
        except Exception as e:
            logger.error(f"❌ 이벤트 발행 실패: {e}")
            return False

# 편의 함수
async def publish_user_event(event_type: EventType, user_id: int, data: dict):
    """사용자 이벤트 발행"""
    event = {
        "event_type": event_type,
        "user_id": user_id,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return await kafka_service.send_event("user_events", event)
```

### 👂 Kafka 컨슈머 (`consumers/user_consumer.py`)

```python
class UserEventConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            'user_events',
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id='user_event_processors',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    async def start_consuming(self):
        """이벤트 소비 시작"""
        await self.consumer.start()
        try:
            async for message in self.consumer:
                await self.process_event(message.value)
        finally:
            await self.consumer.stop()
    
    async def process_event(self, event_data: dict):
        """이벤트 처리"""
        event_type = event_data.get('event_type')
        
        handlers = {
            EventType.USER_CREATED: self._handle_user_created,
            EventType.USER_UPDATED: self._handle_user_updated,
            EventType.USER_LOGIN: self._handle_user_login,
        }
        
        handler = handlers.get(event_type)
        if handler:
            await handler(event_data)
    
    async def _handle_user_created(self, event_data):
        """신규 사용자 생성 처리"""
        user_id = event_data['user_id']
        user_data = event_data['data']
        
        # 1. 환영 이메일 발송 (가상)
        logger.info(f"📧 환영 이메일 발송: {user_data['email']}")
        
        # 2. 초기 설정 생성
        logger.info(f"⚙️ 초기 설정 생성: {user_id}")
        
        # 3. 통계 업데이트
        await self._update_user_stats('new_user')
    
    async def _handle_user_login(self, event_data):
        """사용자 로그인 처리"""
        # 로그인 통계 업데이트
        await self._update_user_stats('login')
```

### 🎯 이벤트 기반 아키텍처의 장점

1. **느슨한 결합 (Loose Coupling)**
   - 사용자 생성 로직과 이메일 발송 로직이 분리
   - 한 서비스의 장애가 다른 서비스에 영향 없음

2. **확장성 (Scalability)**
   - 컨슈머를 여러 개 띄워서 병렬 처리
   - 트래픽에 따라 동적으로 확장

3. **내결함성 (Fault Tolerance)**
   - 메시지 큐에 저장되므로 일시적 장애 시에도 데이터 보존
   - 재시도 메커니즘으로 안정성 확보

4. **비동기 처리**
   - 사용자는 빠른 응답 받고, 후속 처리는 백그라운드에서

---

## 8. 실습 과제

### 🎯 초급 과제

#### 1. **새로운 필드 추가하기**
```python
# 1. User 모델에 nickname 필드 추가
class User(UserBase):
    nickname: Optional[str] = None

# 2. DB 모델에도 추가
class User(Base, TimestampMixin):
    nickname = Column(String(50))

# 3. 마이그레이션 생성
python run_migrations.py generate "add nickname to users"
```

#### 2. **새로운 API 엔드포인트 추가**
```python
@router.get("/users/search")
async def search_users(q: str, limit: int = 10):
    """사용자 이름으로 검색"""
    # 구현해보세요!
    pass
```

### 🎯 중급 과제

#### 1. **캐시 무효화 전략 구현**
```python
async def update_user(user_id: int, user_update: UserUpdate):
    # 1. DB 업데이트
    updated_user = await db_update(user_id, user_update)
    
    # 2. 캐시 무효화 - 어떻게 할까요?
    # 방법 1: 캐시 삭제
    await redis.delete(f"user:{user_id}")
    
    # 방법 2: 캐시 업데이트
    await redis.set(f"user:{user_id}", updated_user.dict())
    
    # 어느 방법이 좋을까요? 언제 어떤 방법을 써야 할까요?
```

#### 2. **페이지네이션 최적화**
```python
async def list_users_optimized(cursor: Optional[int] = None, limit: int = 20):
    """커서 기반 페이지네이션 구현"""
    # OFFSET/LIMIT 대신 커서 기반으로 구현해보세요
    pass
```

### 🎯 고급 과제

#### 1. **분산 트랜잭션 (Saga 패턴)**
```python
async def create_user_with_profile(user_data: UserCreate, profile_data: ProfileCreate):
    """
    사용자 생성 + 프로필 생성을 분산 트랜잭션으로 처리
    
    실패 시나리오:
    1. 사용자는 생성되었는데 프로필 생성 실패
    2. 어떻게 롤백할까?
    """
    pass
```

#### 2. **이벤트 소싱 (Event Sourcing)**
```python
class UserAggregate:
    """
    사용자의 모든 변경을 이벤트로 저장
    현재 상태는 이벤트를 재생해서 구성
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.events = []
        self.current_state = None
    
    def create_user(self, user_data):
        event = UserCreatedEvent(user_data)
        self.events.append(event)
    
    def replay_events(self):
        """이벤트를 재생해서 현재 상태 구성"""
        pass
```

---

## 9. 문제 해결

### 🚨 자주 발생하는 문제들

#### 1. **데이터베이스 연결 문제**
```bash
# 증상: sqlalchemy.exc.OperationalError
# 해결:
docker-compose ps  # PostgreSQL 컨테이너 상태 확인
docker-compose logs postgres  # 로그 확인
```

#### 2. **캐시 일관성 문제**
```python
# 문제: DB는 업데이트했는데 캐시는 예전 데이터
# 해결: 캐시 무효화 패턴 적용

async def update_user(user_id, data):
    try:
        # 1. DB 업데이트
        await db.update(user_id, data)
        
        # 2. 캐시 무효화 (중요!)
        await redis.delete(f"user:{user_id}")
        
    except Exception as e:
        # 롤백 로직
        logger.error(f"업데이트 실패: {e}")
        raise
```

#### 3. **Kafka 메시지 중복 처리**
```python
class UserEventConsumer:
    def __init__(self):
        self.processed_events = set()  # 처리된 이벤트 ID 저장
    
    async def process_event(self, event_data):
        event_id = event_data.get('event_id')
        
        # 중복 처리 방지
        if event_id in self.processed_events:
            logger.info(f"이미 처리된 이벤트: {event_id}")
            return
        
        # 처리 로직
        await self.handle_event(event_data)
        
        # 처리 완료 마킹
        self.processed_events.add(event_id)
```

### 🔍 디버깅 팁

#### 1. **로그 활용하기**
```python
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 중요 지점에 로그 추가
async def create_user(user_data):
    logger.info(f"사용자 생성 시작: {user_data.email}")
    
    try:
        # ... 처리 로직
        logger.info(f"사용자 생성 완료: {user.id}")
        return user
    except Exception as e:
        logger.error(f"사용자 생성 실패: {e}", exc_info=True)
        raise
```

#### 2. **데이터베이스 쿼리 최적화**
```python
# 문제: N+1 쿼리
users = await session.execute(select(User))
for user in users:
    activities = await session.execute(
        select(UserActivity).where(UserActivity.user_id == user.id)
    )  # 사용자마다 별도 쿼리 실행! (비효율)

# 해결: JOIN 사용
stmt = select(User).options(selectinload(User.activities))
users = await session.execute(stmt)
# 한 번의 쿼리로 모든 데이터 가져오기
```

#### 3. **성능 모니터링**
```python
import time
from functools import wraps

def measure_time(func):
    """실행 시간 측정 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            logger.info(f"{func.__name__} 실행시간: {end_time - start_time:.2f}초")
    return wrapper

@measure_time
async def get_user(user_id: int):
    # 이 함수의 실행 시간이 자동으로 로그에 출력됨
    return await user_service.get_user(user_id)
```

---

## 🎓 학습 로드맵

### 1주차: 기초 이해
- [ ] 전체 아키텍처 파악
- [ ] FastAPI 기본 개념
- [ ] PostgreSQL + SQLAlchemy 기초
- [ ] 간단한 CRUD API 구현

### 2주차: 중급 패턴
- [ ] 캐시 전략 이해 및 구현
- [ ] JWT 인증 시스템
- [ ] 에러 처리 및 로깅
- [ ] 데이터 검증 및 보안

### 3주차: 고급 아키텍처
- [ ] 이벤트 기반 아키텍처
- [ ] Kafka 프로듀서/컨슈머
- [ ] 분산 시스템 패턴
- [ ] 성능 최적화

### 4주차: 실전 프로젝트
- [ ] 복잡한 비즈니스 로직 구현
- [ ] 테스트 코드 작성
- [ ] 모니터링 및 로깅
- [ ] 배포 및 운영

---

## 📚 추천 추가 학습 자료

### 📖 공식 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 문서](https://pydantic-docs.helpmanual.io/)
- [Apache Kafka 문서](https://kafka.apache.org/documentation/)

### 🎥 온라인 강의
- FastAPI 완전정복
- PostgreSQL 성능 최적화
- Kafka 실무 적용
- 마이크로서비스 아키텍처

### 📚 도서 추천
- "마이크로서비스 패턴" - 크리스 리처드슨
- "데이터 중심 애플리케이션 설계" - 마틴 클렙만
- "클린 아키텍처" - 로버트 C. 마틴

---

## 🎯 마무리

이 가이드를 통해 현대적인 웹 애플리케이션 개발의 핵심 개념들을 학습하실 수 있습니다:

✅ **FastAPI**로 고성능 API 개발
✅ **PostgreSQL**로 안정적인 데이터 저장
✅ **Redis**로 효율적인 캐시 전략
✅ **Kafka**로 확장 가능한 이벤트 처리
✅ **JWT**로 보안 인증 시스템
✅ **SQLAlchemy 2.0**으로 현대적인 ORM 사용

**학습 팁:**
1. 코드를 직접 실행해보며 이해하기
2. 로그를 확인하며 데이터 흐름 추적하기
3. 작은 변경부터 시작해서 점진적 확장하기
4. 에러를 두려워하지 말고 디버깅 연습하기

화이팅! 🚀