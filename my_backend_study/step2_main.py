from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Intenger, String, datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy,orm import sessionmaker, Sessiion
from typing import List
from datetime import datetime

# 데이터 베이스 설정
DATABASE_URL = "postgresql://username:password@localhost:5432/my_backend_db"

# 데이터베이스 엔진 생성
engine = create_engin(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,
autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 모델(테이블 구조)
class Userdb(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# 테이블 생성
Base.metadata.create_all(bind=engine)

# pydantic 모델(api 입출력용)
class UserCreate(BaseModel):
    name:str
    email:str
    age:int
    created_at: datetime

    class Config:
        from_attributes = True # sqlalchemy 모델 -> pydantic 변환 허용

# 데이터베이스 세션 관리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
# fastapi 앱생성
app = FastAPI()

# 홈페이지
@app.get("/")
def read_user(db: Sessiion = Depends(get_db)):
    total_users = db.query(UserDB).count()
    return {
        "message": "PostgreSQL 연동 사용자 관리 api",
        "total_users": total_users,
        "database": "PostgreSQL 연결됨"
    }

# 모든 사용자 조회
@app.get("/users", response_model=List[User])
def get_all_users(db:Sessiion =Depends(get_db)):
    users = db.query(UsersDB).all()
    return users

# 특정 사용자 조회
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session= 
Depends(get_db)):
    # id로 특정 사용자 조회
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, 
detail="사용자를 찾을수 없습니다")

# 새 사용자 생성
@app.post("/users", response_model=User)
def create_user(user_data: UserCreate, db: Session =
Depends(get_db)):

    # 이메일 중복체크
    existing_user = 
db.query(UserDB).filter(UserDB.email == 
user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400,
        detail="이미존재하는 이메일입니다")

    # 새사용자 생성
    new_user = UserDB(
        name_user_data.name,
        email=user_data.email,
        age=user_data.age
    )

    # 데이터베이스 저장
    db.add(ne_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# 사용자 삭제 
@app.delete("/users/{user_id}}")
def delete_user(user_id: int, db: Session =
Depends(get_db)):

    # 사용자 찾기
    user -db.query(UserDB).filter(UserDB.id == 
    user_id).first()
    if not user:
        raise HTTPEsception(status_code=404,
    detail="사용자 찾을수없다")

    user_name =user.name
    db.delete(user)
    db.commit()

    return {"message": f"{user_name}님 이 삭제되었습니다"}