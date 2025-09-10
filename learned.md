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