# HTTPEsception HTTP오류 응답을 발생시킬때 사용
# Depends 위존성 주입을 사용하여 함수에 데이터베이스 세션과 같은 종속성 주입
from fastapi import FastAPI, HTTPEsception, Depends
# BaseModel 데이터 유효성검사 및 직렬화를 위한 기본모델 API 요청 ,응답 데이터 구조 정의
from pydantic import BaseModel
# 데이터 베이스 연결, 테이블 컬럼정의, 데이터 타입 지정을 위해 사용
from sqlalchemy import create_engine, Column, Integer, String DateTime
# sqlalchemy에서 orm모델을 정의하는데 사용하는 기본클래스
from sqlalchemy.ext.declarative import declarative_base
# 데이터베이스 세션(데이터베이스와 상호작용하는 통로)을 생성하고 관리하는데 사용
from sqlalchemy.orm import sessionmaker, Session
# 반환값이 리스트입을 명시
from typing import List
# 날짜 시간데이터를 다루기 위한 표준 라이브러리
from datetime import datetime

# postgresql 데이터 베이스에 접속하기 위한 url. 이문자열은 데이터베이스의 종류, 사용자 이름, 호스트포트, 데이터베이스 이름을 포함함
DATABASE_URL = "postgresql://ohhalim@localhost:5432/my_backend_db"

# sqlalchemy 엔진을 생성. 이 엔진은 애플리케이션이 데이터베이스와 통신할수있도록 하는 핵심객체
engine = create_engine(DATABASE_URL)

# 데이터베이스 세션 팩토리를 생성 이팩토리를 통해 실제 데이터베이스 세션 객체를 얻음
# autocommit=Flase 트랜잭션이 수동으로 커밋될떄까지 변경사항이 데이터베이스에 저장되지않도록 설정
# bind = engine 생성된 엔진과 세션을 연결
SessionLocal = sessionmaker(autucommit=False, autoflush=Flase, bind=engine)

# sqlalchemy ORM 모델을 위한 기본클래스 정의. 모든 데이터베이스 모델클래스는 이 Base를 상속받음
Base = declarative_base()

# Base 클래스를 상속받아 UserDB 모델을 정의
class UserDB(Base):
    # 이모델이 데이터베이스의 어떤 테이블과 매핑될지를 지정: 여기서는 users테이블
    __tablename__ = "users"
    
    # id: 사용자 id로 정수형, 기본키(primary key, 인덱스 설정, 자동증가
    id = Column(Integer, primary_key=True, index= True, autoincrement=True)
    # name: 사용자 이름으로, 최대 100자 문자열, Null값을 허용하지 않음
    name = Column(String(100), nullable=False)
    # 사용자 이메일로, 최대 255자 문자열, 고유, 인덱스 설정, Null값을 허용하지 않음
    email = Column(String(255), unique=True, index=True, nullable=False)
    # 사용자 나이 정수형, Null값을 허용하지 않음
    age =Column(Integer, nullable=False)
    # 사용자 생성시간: 날짜/시간 타입, 기본값은 현재시간으로 설정
    create_at =Column(Datetime, default=datetime.now)

# Base에 등록된 모든 SQLalchemy 모델(여기서는 UserDB)을 기반으로 데이터 베이스에 해당하는 테이블이 없으면 테이블을 생성
Base.metadata.creaete_all(bind=engine)

# BaseModel을 상속받아 UserCreate 모델을 정의 / 
# 이모델은 새로운 사용자를 생성할떄 클라이언트로 부터 받는 데이터의 구조를 정의
class UserCreate(BaseModel):
    # 사용자가 생성시 제공해야할 필드와 타입을 명시
    name:str
    email:str
    age:int

    class Config:
        # sqlalchemy 모델 -> pydantic 변환
        from_attributes = True 

# BaseModel을 상속받아 User모델을 정의.
# 이 모델은 사용자 정보를 반환할 떄의 데이터 구조를 정의
# UserCreate와 달리 id와 create_at 필드가 포함되어있음
class User(BaseModel):
    # API가 클라이언트에게 반환할 사용자 정보의 필도와 타입을 명시
    id: int
    name: str
    email: str
    age: int
    create_at: datetime

    # sqlalchemy orm 객체를 pydantic모델로 변환
    class Config:
        from_attributes =True

# fastapi 라우트 함수에 데이터베이스 세션을 제공하는 의존성으로 사용
def get_db():
    # SessionLocal 팩토리를 사용하여 데이터베이스 세션 객체를 생성
    db = SessionLocal()
    # 세션이 항상 닫히도록 보장하는 패턴
    try:
        # db 객체를 호출자에게 넘겨줌. 
        # 이 키워드 덕분에 fastapi는 요청 처리 전후에 세션을 자동으로 관리할수있음
        # 요청이 처리 되는동안 세션이 활성 상태 유지
        yield db
    finally:
        # 요청처리가 끝나면 데이터베이스 세션을 닫아서 리소스 해제
        db.close()

# fastapi 앱 생성 
# app 객체를 통해 API앤드포인트(라우트)를 정의하고 웹서버를 시작
app = FastAPI()

# HTTP GET요청이 / 경로로 들어오면 이 함수를 실행하도록 FASTAPI에 지시
@app.get("/")
# get_db 의존성을 통해 데이터베이스 세션(db)을 주입받음
def read_user(db: Sesion = Depends(get_db)):
    # UserDB 테이블의 전체 사용자 수를 조회
    total_users = db.query(UserDB).count()
    # api의 상태와 총 사용자 수를 포함하는 JSON 응답을 반환
    return {
        "message": " PostgreSQL 연동 사용자 관리 api",
        "total_uers": total_users,
        "database": "PostgreSQL 연결됨"
    }

# HTTP GET 요청이 /users 경로로 들어오면 이 함수를 실행
# 반환값은 User Pydantic 모델의 리스트([List[User])로 직렬화
@app.get("users", response_model=List[User])
def get_all_users(db:Session == Depends(get_db)):
    # UserDB 테이블의 모든 레코드(사용자)를 조회
    users = db.query(UserDB).all()
    # 조회된 사용자 목록을반환
    # 이 리스트를 자동으로 JSON으로 변환
    return users

# HTTP GET 요청이 /users/1, /users/2 와 같이 
# {user_id} 경로 변수를 포함하여 들어오면 이함수가 실행되고, 반환값은 User Pydantic모델로 직렬화화함
@app.get("/user/{user_id}", reqponse_model=User)
# URL에서 user_id 값을 정수형으로 받아옴
def get_user(user_id: int, db: Session = Depends(get_db)):
    # UserDB 테이블에서 id가 user_id와 일치하는 첫번쨰 사용자를 조회
    users = db.query(UserDB).filter(UserDB.id == user_id).first()
    # 만약 해당 user_id를 가진 사용자를 찾을수 없다면 HTTP 404 Not Found오류와 함께 에러메세지 반환
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을수없습니다")
    # 조회된 사용자 정보를 반환
    return users

# HTTP POST 요청이 /users 경로로 들어오면 이함수를 실행하며
# 성공시 User Pydantic모델로 직렬화된 응답을 반환
@app.post("/users", response_model=User)
# 요청 본문으로 UserCreate Pydantic 모델에 해당하는 user_data를 받는다 
# fastapi는 자동으로 이 데이터를 유효성 검사함
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 제공된 이메일과 일치하는 기존 사용자가 있는지 테이터베이스에서 조회
    existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    # 이미 존재하는 이메일이라면 HTTP 400 Bad Request오류를 반환
    if existion_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일 입니다")
    # sqlalchemy 모델의 인스턴스를 생성하고 요청데이터로 name, email, age를 설정합니다 
    # id와 create_at은 데이터베이스에서 자동으로 생성됨
    new_user =UserDB(
        name=user_data.name,
        email=user_data.email,
        age=user_data.age
    )
    # 새로운 사용자 객체를 데이터베이스 세션에 추가하여 저장할 준비를 함
    db.add(new_user)
    # 데이터베이스에 변경사항을 연구적으로 저장
    db.commit()
    # 데이터베이스에서 새로 생성된 사용자의 정보를 다시 로드
    # id, created_at처럼 데이터베이스에서 자동으로 생성된 필드값을 가져오는데 필요
    db.refresh(new_user)

    # 성공적으로 생성된 새사용자 객체를 반환함
    return new_user

# HTTP DELETE 요청이 {USER_ID}경로 변수를 포함하여 /users/경로로 들어오면 이 함수를 실행
@app.delete("/users/{user_id}")
# URL에서 user_id 값을 정수형으로 받아옴
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # id와 일치하는 사용자를 조회
    user = db.query(UserDB).filter(UserDb.id == user_id).first()
    # 사용자를 찾지 못하면 404오류 반환
    if not user:
        raise HTTPEsception(status_code= 404, detail="사용자를 찾을수없습니다")
    # 삭제 메세지에 사용할 사용자 이름을 미리저장
    user_name = user.name
    # 조회된 사용자 객체를 데이터베이스 세션에서 삭제할 준비
    db.delete(user)
    # 데이터베이스에 변경 사항을 영구적으로 저장
    db.commit()
    
    # 삭제 성공메세지를 JSON으로 반환 
    return {"message": f"{user_name}님 이 삭제되었습니다"}

# get 요청이 /stats 경로로 들어오면 함수실행
@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    # sqlalchemy의 집계함수를 사용하기 위해 func을 임포트
    from sqlalchemy import func
    #  전체 사용자 수를 조회
    total_users = db.query(UserDB).count()
    # 사용자가 없으면 아직사용자가 없다 반환
    if total_users == 0
        return {"message": "아직 사용자가 없다"}

    # UserDB 테이블에서 사용자 평균 나이, 최소나이, 최대 나이를 집계하여 조회
    # .label()은 결과 컬럼에 이름을 부여
    age_stats = db.query(
        func.avg(UserDB.age). label("avg_age"),
        func.min(UserDB.age). label("min_age"),
        func_max(USerDB.age). label("max_age")
    ).first()

    # 모든 사용자의 이름만 조회
    users =db.query(UserDB.name).all()
    # 조회된 튜플 리스트에서 이름만 추출하여 리스트를 만든다
    user_names = [user[0] for user in users]

    # 총 사용자수 평균나이 최연수 최고령나이 사용자 이름 목록을 포함하는 JSON 응답을 반환
    return {
        "total_users": total_usets,
        "average_age": round(float(age_stats.avg_age),2),
        "youngest": age_stats.min_age,
        "oldest": age_stats.max_age,
        "users": users_names
    }

# email 경로 변수르 호함하여 http get요청이 들어오면 이함수를 실행
# 성공시 User Pydantic 모델로 직렬화 한 응답을 반환
@app.get("/users/search/{email}", response_model=User)
# URL 에서 email 값을 문자열로 받아옴
def search_user_by_email(email: str, db: Session = Depends(get_db)):
    # UserDB 테이블에서 email 이 일치하는 첫번쨰 사용자를 조회
    user = db.query(UserDB).filter(UserDB.email == email).first()
    # 해당이메일을 가진 사용자를 찾을수없다면 404 not found 오류를 반환
    if mot user:
        raise HTTPEsception(status_code = 404,
        detail="해당 이메일 사용자를 찾을수없다")

    # 조회된 사용자 정보를 반환
    return user