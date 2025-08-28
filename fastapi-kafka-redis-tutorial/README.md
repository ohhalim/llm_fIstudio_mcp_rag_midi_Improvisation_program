# FastAPI + Kafka + Redis + PostgreSQL 튜토리얼 💚⚡🔴🐘

현대적인 마이크로서비스 아키텍처를 학습하기 위한 실습용 프로젝트입니다.

## 🎯 학습 목표

이 프로젝트를 통해 다음을 배울 수 있습니다:

- **FastAPI**: 현대적인 Python 웹 프레임워크
- **PostgreSQL**: 강력한 관계형 데이터베이스
- **SQLAlchemy 2.0**: 최신 비동기 ORM
- **Redis**: 고성능 인메모리 캐시 및 데이터 저장소
- **Apache Kafka**: 실시간 이벤트 스트리밍 플랫폼
- **이벤트 기반 아키텍처**: 마이크로서비스 간 비동기 통신
- **캐시 패턴**: Cache-Aside, Write-Through 등
- **API 설계**: RESTful API 설계 원칙
- **데이터베이스 마이그레이션**: Alembic을 이용한 스키마 관리
- **JWT 인증**: bcrypt와 JWT를 이용한 보안

## 🏗️ 아키텍처 개요

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

## 📂 프로젝트 구조

```
fastapi-kafka-redis-tutorial/
├── main.py                 # FastAPI 애플리케이션 메인 파일
├── config.py              # 설정 관리 (PostgreSQL, JWT 포함)
├── models.py              # Pydantic 데이터 모델
├── db_models.py           # SQLAlchemy ORM 모델
├── database.py            # 데이터베이스 연결 관리
├── requirements.txt       # Python 의존성 (PostgreSQL 포함)
├── docker-compose.yml     # Docker 컨테이너 설정 (PostgreSQL 포함)
├── .env                   # 환경변수 (DB URL, JWT 시크릿)
├── alembic.ini           # Alembic 마이그레이션 설정
├── run_migrations.py     # 마이그레이션 실행 스크립트
├── README.md             # 이 파일
│
├── services/             # 비즈니스 로직 서비스
│   ├── __init__.py
│   ├── auth_service.py   # JWT 인증 서비스 (bcrypt 포함)
│   ├── redis_service.py  # Redis 캐시 서비스
│   ├── kafka_service.py  # Kafka 메시징 서비스
│   └── user_service.py   # 사용자 비즈니스 로직 (PostgreSQL 연동)
│
├── routers/              # API 라우터
│   ├── __init__.py
│   ├── users.py          # 사용자 관련 API
│   └── events.py         # 이벤트 관련 API
│
├── consumers/            # Kafka 컨슈머
│   ├── __init__.py
│   └── user_consumer.py  # 사용자 이벤트 처리
│
└── migrations/          # 데이터베이스 마이그레이션
    ├── env.py           # Alembic 환경 설정
    ├── script.py.mako   # 마이그레이션 템플릿
    └── versions/        # 마이그레이션 버전들
        └── 001_initial_migration.py  # 초기 스키마
```

## 🚀 빠른 시작

### 1. 프로젝트 클론 및 의존성 설치

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Docker로 PostgreSQL, Redis, Kafka 실행

```bash
# Docker Compose로 모든 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 서비스 준비 완료까지 대기 (약 30초)
sleep 30
```

서비스 접근 주소:
- **PostgreSQL**: `localhost:5432` (사용자: tutorial_user, 비밀번호: tutorial_password)
- **Redis**: `localhost:6379`
- **Kafka**: `localhost:9092`
- **Kafka UI**: `http://localhost:8080`
- **Redis Insight**: `http://localhost:8001`

### 3. 데이터베이스 초기화 및 마이그레이션

```bash
# 데이터베이스 스키마 초기화 및 마이그레이션 실행
python run_migrations.py init

# 또는 단계별로 실행
python run_migrations.py upgrade  # 마이그레이션만 실행
python run_migrations.py current  # 현재 버전 확인
```

### 4. FastAPI 애플리케이션 실행

```bash
# 개발 서버 시작
python main.py

# 또는 uvicorn 직접 사용
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Kafka Consumer 실행 (별도 터미널)

```bash
# 사용자 이벤트 컨슈머 시작
python consumers/user_consumer.py
```

## 📚 API 사용법

애플리케이션이 시작되면 다음 주소에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 주요 엔드포인트

#### 🧑‍💼 사용자 관리
```bash
# 사용자 생성
curl -X POST \"http://localhost:8000/api/v1/users/\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"name\": \"홍길동\",
    \"email\": \"hong@example.com\",
    \"password\": \"password123\",
    \"age\": 25,
    \"phone\": \"01012345678\"
  }'

# 사용자 조회
curl \"http://localhost:8000/api/v1/users/1\"

# 사용자 목록 조회
curl \"http://localhost:8000/api/v1/users/?skip=0&limit=10\"

# 사용자 로그인
curl \"http://localhost:8000/api/v1/users/auth/login?email=hong@example.com&password=password123\"
```

#### 📨 이벤트 처리
```bash
# 사용자 이벤트 발행
curl -X POST \"http://localhost:8000/api/v1/events/user-events?event_type=user_created&user_id=1\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"message\": \"새 사용자 환영\"}'

# 토픽 목록 조회
curl \"http://localhost:8000/api/v1/events/topics\"

# 새 토픽 생성
curl -X POST \"http://localhost:8000/api/v1/events/topics?topic_name=custom_events&num_partitions=3\"
```

#### 🔍 모니터링
```bash
# 전체 헬스체크
curl \"http://localhost:8000/health\"

# 애플리케이션 메트릭
curl \"http://localhost:8000/metrics\"

# 사용자 통계
curl \"http://localhost:8000/api/v1/users/stats/overview\"
```

## 🔧 개발 가이드

### 데이터베이스 관리

#### 마이그레이션 관리
```bash
# 새 마이그레이션 생성
python run_migrations.py generate "add user profile table"

# 마이그레이션 적용
python run_migrations.py upgrade

# 이전 버전으로 롤백
python run_migrations.py downgrade 001

# 마이그레이션 히스토리 확인
python run_migrations.py history
```

#### 데이터베이스 직접 접근
```bash
# PostgreSQL 컨테이너 접속
docker-compose exec postgres psql -U tutorial_user -d fastapi_tutorial

# 테이블 확인
\dt

# 사용자 테이블 조회
SELECT * FROM users;
```

### 코드 구조 이해하기

#### 1. **서비스 레이어 패턴 (PostgreSQL 연동)**
```python
# services/user_service.py
class UserService:
    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        async with get_async_session() as session:
            # 1. 이메일 중복 확인 (DB)
            # 2. 비밀번호 해싱 (bcrypt)
            # 3. 사용자 정보 저장 (PostgreSQL)
            # 4. 캐시 저장 (Redis)
            # 5. 이벤트 발행 (Kafka)
            # 6. 활동 로그 기록 (DB)
```

#### 2. **캐시-어사이드 패턴 (PostgreSQL + Redis)**
```python
async def get_user(self, user_id: int) -> Optional[User]:
    # 1. 캐시에서 먼저 조회
    cached_user = await redis_service.get_user_cache(user_id)
    if cached_user:
        return User(**cached_user)
    
    # 2. 캐시 미스 - PostgreSQL에서 조회
    async with get_async_session() as session:
        stmt = select(DBUser).where(DBUser.id == user_id)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            user = User(id=db_user.id, name=db_user.name, ...)
            # 3. 캐시에 저장
            await redis_service.set_user_cache(user_id, user.dict())
            return user
```

#### 3. **이벤트 기반 아키텍처**
```python
# 이벤트 발행
await kafka_service.send_event('user_events', event)

# 이벤트 처리 (Consumer)
async def _handle_user_created(self, event_data):
    # 환영 이메일 발송
    # 초기 설정 생성
    # 로그 기록
```

### 주요 학습 포인트

#### 🎯 **FastAPI + PostgreSQL 핵심 개념**
- **의존성 주입**: `Depends()` 를 통한 DB 세션 주입
- **데이터 검증**: Pydantic 모델을 통한 자동 검증
- **에러 처리**: HTTPException과 전역 예외 처리기
- **미들웨어**: 요청/응답 처리 파이프라인
- **라이프사이클**: startup/shutdown 이벤트
- **ORM 패턴**: SQLAlchemy 2.0 비동기 ORM 사용
- **트랜잭션 관리**: 세션과 커밋/롤백 관리

#### 🐘 **PostgreSQL + SQLAlchemy 패턴**
- **모델 정의**: SQLAlchemy 모델과 Pydantic 모델 분리
- **비동기 쿼리**: async/await 패턴의 데이터베이스 쿼리
- **관계 매핑**: 외래 키와 관계 설정
- **인덱싱**: 성능을 위한 데이터베이스 인덱스 설계
- **마이그레이션**: Alembic을 통한 스키마 버전 관리

#### 🔐 **JWT 인증 패턴**
- **비밀번호 해싱**: bcrypt를 이용한 안전한 비밀번호 저장
- **토큰 생성**: JWT 액세스/리프레시 토큰 발급
- **토큰 검증**: 미들웨어를 통한 자동 인증
- **권한 관리**: 역할 기반 접근 제어

#### 🔴 **Redis 활용 패턴**
- **캐시-어사이드**: 애플리케이션이 캐시를 직접 관리
- **TTL 관리**: 적절한 만료시간 설정
- **네임스페이싱**: `user:123` 형태의 키 네이밍
- **데이터 직렬화**: JSON 기반 객체 저장

#### ⚡ **Kafka 메시징 패턴**
- **Producer**: 이벤트 발행과 배치 처리
- **Consumer**: 이벤트 구독과 처리
- **토픽 관리**: 파티션과 복제본 설정
- **에러 처리**: 재시도와 데드레터큐

### 코드 확장하기

#### 1. **새로운 도메인 추가**
```bash
# 1. 모델 정의 (models.py에 추가)
class Product(BaseModel):
    name: str
    price: float

# 2. 서비스 생성
# services/product_service.py

# 3. 라우터 생성
# routers/products.py

# 4. 메인 앱에 라우터 등록
```

#### 2. **새로운 이벤트 타입 추가**
```python
# models.py에 이벤트 타입 추가
class EventType(str, Enum):
    PRODUCT_CREATED = \"product_created\"
    ORDER_PLACED = \"order_placed\"

# 컨슈머에 핸들러 추가
async def _handle_product_created(self, event_data):
    # 제품 생성 후속 처리
```

## 🧪 테스트

### 단위 테스트 실행
```bash
# pytest 설치
pip install pytest pytest-asyncio

# 테스트 실행
pytest tests/ -v
```

### API 테스트 (HTTPie 사용)
```bash
# HTTPie 설치
pip install httpie

# 사용자 생성 테스트
http POST localhost:8000/api/v1/users/ \\
  name=\"테스트사용자\" \\
  email=\"test@example.com\" \\
  password=\"testpass123\" \\
  age:=30
```

## 🐛 문제 해결

### 자주 발생하는 문제들

#### 1. **Docker 서비스 연결 실패**
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs redis
docker-compose logs kafka

# 서비스 재시작
docker-compose restart
```

#### 2. **Kafka 연결 타임아웃**
```bash
# Kafka 준비 대기 (최대 60초)
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

#### 3. **Redis 연결 실패**
```bash
# Redis 연결 테스트
docker-compose exec redis redis-cli ping
```

#### 4. **Python 의존성 문제**
```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 로그 확인
```bash
# 애플리케이션 로그
tail -f app.log

# 컨슈머 로그
tail -f consumer.log

# Docker 로그
docker-compose logs -f
```

## 📊 모니터링 및 관리 도구

### Web UI 도구들
- **Kafka UI**: `http://localhost:8080`
  - 토픽, 파티션, 메시지 관리
  - 컨슈머 그룹 모니터링
  
- **Redis Insight**: `http://localhost:8001`
  - Redis 데이터 브라우징
  - 성능 모니터링

- **API 문서**: `http://localhost:8000/docs`
  - 대화형 API 테스트
  - 스키마 확인

### CLI 도구들
```bash
# Kafka 토픽 관리
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic user_events

# Redis CLI
docker-compose exec redis redis-cli
docker-compose exec redis redis-cli KEYS \"user:*\"
```

## 🚀 프로덕션 배포

### 환경별 설정
```bash
# 개발 환경
export DEBUG=true
export REDIS_URL=redis://localhost:6379

# 프로덕션 환경
export DEBUG=false
export REDIS_URL=redis://prod-redis:6379
export SECRET_KEY=your-secure-secret-key
```

### Docker 빌드
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD [\"gunicorn\", \"main:app\", \"-w\", \"4\", \"-k\", \"uvicorn.workers.UvicornWorker\"]
```

## 📚 추가 학습 자료

### 공식 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Redis 공식 문서](https://redis.io/documentation)
- [Apache Kafka 공식 문서](https://kafka.apache.org/documentation/)

### 심화 주제
- **보안**: JWT 인증, OAuth2, CORS 설정
- **성능**: 연결 풀링, 캐시 최적화, 비동기 처리
- **확장성**: 로드 밸런싱, 클러스터링, 샤딩
- **모니터링**: Prometheus, Grafana, ELK 스택

### 실제 프로젝트 적용
1. **전자상거래**: 주문 처리, 재고 관리, 결제 시스템
2. **소셜미디어**: 실시간 피드, 알림 시스템, 메시징
3. **IoT 플랫폼**: 센서 데이터 수집, 실시간 분석
4. **금융 시스템**: 거래 처리, 사기 탐지, 리스크 관리

## 🤝 기여하기

이 프로젝트는 학습 목적으로 만들어졌습니다. 개선 사항이나 버그를 발견하시면 언제든지 기여해주세요!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 감사의 말

이 튜토리얼은 다음 오픈소스 프로젝트들을 기반으로 작성되었습니다:
- [FastAPI](https://github.com/tiangolo/fastapi)
- [Redis](https://github.com/redis/redis)
- [Apache Kafka](https://github.com/apache/kafka)

---

**Happy Coding! 🎉**

궁금한 점이 있으시면 언제든지 이슈를 남겨주세요!