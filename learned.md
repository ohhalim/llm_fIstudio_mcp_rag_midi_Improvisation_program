```
main.py fastapi 앱 생성 , 기본라우터
config.py 환경변수 관리 , 설정 중앙화
database.py db연결 관리 , 세션관리(매 요청마다 db연결) 테이블 생성
엔진: db와 실제연결
세션: db 작업을 위한 임시연결
base: 모든 테이블모델의 부모클래스
model.py db테이블 구조 정의 python 객체 <->  db 테이블 매핑 / sqlalchemy orm사용
schemas.py api 요청/응답 데이터 검증. 자동 타입변환 
잘못된 데이터가 들어오면 자동 에러 -> pydantic 이 자동으로 검증에러 반환
repository.py db쿼리 집중관리 / 재사용 가능한 db함수들/ service계층과db분리
service.py 비즈니스 규칙 구현 / 에러처리/ 복잡한 로직처리
비즈니스 로직의 역할 / 데이터 검증, 중복체크, 권한확인, 복잡한 계산
controller.py / http 요청/응답처리, url 라우팅
```

----

요청이 들어올떄 
HTTP 요청 → Controller → Service → Repository → Model → Database

응답이 나갈때 
Database → Model → Repository → Service → Controller → HTTP 응답

``` python
# 1. 사용자가 API 호출
POST /api/v1/users/
{"name": "홍길동", "email": "hong@example.com"}

# 2. Controller에서 수신
@router.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_new_user(db, user)

# 3. Service에서 비즈니스 로직
def create_new_user(db, user):
    if get_user_by_email(db, user.email):
        raise HTTPException(400, "Email already exists")
    return create_user(db, user)

# 4. Repository에서 DB 저장
def create_user(db, user):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    return db_user
```

----

Python 객체 ↔ DB 테이블 매핑이란?

python 클래스를 데이터베이스 테이블로 자동변환하는 기술

``` python
# Python 코드
  user = User(name="김철수",
  email="kim@test.com", age=25)
  db.add(user)
  db.commit()

  자동으로 SQL 실행됨:
  INSERT INTO users (name, email, age,
  created_at)
  VALUES ('김철수', 'kim@test.com', 25,
  '2024-01-01 10:00:00');

  데이터 조회:
  # Python 코드
  user = db.query(User).filter(User.email ==
  "kim@test.com").first()
  print(user.name)  # "김철수"

  자동으로 SQL 실행됨:
  SELECT * FROM users WHERE email =
  'kim@test.com' LIMIT 1;
```

sql 몰라도 db조작가능
타입검사로 오류 방지
db데이터를 객체로 다룬다
sql을 자동생성
  1. 모델 정의 (model.py): Python 클래스로
  테이블 구조 정의
  2. 자동 테이블 생성 (database.py):
  Base.metadata.create_all()로 실제 테이블
  생성
  3. 데이터 조작 (repository.py): Python
  객체로 DB 조작
  4. 자동 SQL 생성: SQLAlchemy가 뒤에서 SQL
  자동 생성

----


⏺ 🏗️ /app 디렉터리 완전 분석

  📁 전체 구조 (레이어드 아키텍처)

  app/
  ├── 🔧 config.py      ← 설정 관리
  ├── 📊 schemas.py     ← 데이터 검증 (API
  입출력)
  ├── 🗄️ model.py       ← DB 테이블 정의
  ├── 🔗 database.py    ← DB 연결 설정
  ├── 📦 repository.py  ← DB 직접 조작 (SQL)
  ├── 🧠 service.py     ← 비즈니스 로직
  ├── 🌐 controller.py  ← API 엔드포인트
  └── 🚀 main.py        ← 앱 시작점

  📝 각 파일의 역할

  1. 🔧 config.py - 설정 관리자

  # 앱의 모든 설정을 한곳에서 관리
  DATABASE_URL = "sqlite:///./simple_app.db"
  # DB 위치
  APP_NAME = "Simple FastAPI App"
   # 앱 이름
  DEBUG = True
   # 디버그 모드
  역할: 환경변수, DB 주소, 앱 설정 등 모든
  설정을 중앙에서 관리

  2. 📊 schemas.py - 데이터 검증기

  # API로 들어오는/나가는 데이터의 형태를 정의
  UserCreate:    name, email, age     ← 사용자
   생성시 받는 데이터
  UserResponse:  id, name, email...   ← API가
  반환하는 데이터
  UserUpdate:    name?, email?, age?  ←
  업데이트시 받는 데이터 (선택적)
  역할: API 입출력 데이터의 형태와 검증 규칙
  정의

  3. 🗄️ model.py - DB 테이블 설계도

  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True)
    # 사용자 ID
      name = Column(String(50))
    # 이름 (최대 50자)
      email = Column(String(100), unique=True)
    # 이메일 (중복 불가)
      age = Column(Integer)
    # 나이
  역할: 실제 DB 테이블의 구조를 Python
  클래스로 정의

  4. 🔗 database.py - DB 연결 관리자

  # SQLite DB에 연결하고 세션을 관리
  engine = create_engine(DATABASE_URL)
   # DB 엔진
  SessionLocal = sessionmaker(bind=engine)
   # DB 세션 팩토리
  get_db() → db 세션
  # API에서 DB 사용할 때 호출
  역할: DB 연결, 세션 관리, 테이블 생성

  5. 📦 repository.py - DB 조작 전문가

  # 실제 DB와 대화하는 함수들
  get_user(id) → 사용자 한명 조회
  get_users() → 사용자 목록 조회
  create_user() → 새 사용자 생성
  update_user() → 사용자 정보 수정
  delete_user() → 사용자 삭제
  역할: DB에 직접 명령하는 CRUD 함수들

  6. 🧠 service.py - 비즈니스 로직 처리

  class UserService:
      create_new_user():
          1. 이메일 중복 체크    ← 비즈니스
  규칙
          2. 사용자 생성        ← repository
  호출
          3. 에러 처리          ← 예외 상황
  처리
  역할: 비즈니스 규칙, 데이터 검증, 에러 처리

  7. 🌐 controller.py - API 엔드포인트

  @router.post("/users/")     → 사용자 생성 
  API
  @router.get("/users/")      → 사용자 목록 
  API  
  @router.get("/users/{id}")  → 특정 사용자 
  API
  @router.put("/users/{id}")  → 사용자 수정 
  API
  @router.delete("/users/{id}") → 사용자 삭제 
  API
  역할: HTTP 요청을 받아서 적절한 service 함수
   호출

  8. 🚀 main.py - 앱 시작점

  app = FastAPI()                    # FastAPI
   앱 생성
  app.include_router(router)         # API 
  라우터 등록
  @app.on_event("startup") → 테이블 생성  # 앱
   시작시 DB 테이블 생성
  역할: 앱 초기화, 라우터 등록, 시작 이벤트
  처리

  🔄 데이터 흐름 (사용자 생성 예시)

  1. 클라이언트 → controller.py
     POST /users/ {"name": "김철수", "email":
  "kim@test.com"}

  2. controller.py → schemas.py
     UserCreate로 데이터 검증 ✅

  3. controller.py → service.py
     UserService.create_new_user() 호출

  4. service.py → repository.py
     이메일 중복 체크 → get_user_by_email()
     사용자 생성 → create_user()

  5. repository.py → model.py → database.py
     User 객체 생성 → DB에 저장

  6. 응답 역순으로 전달
     database.py → repository.py → service.py
  → controller.py → 클라이언트