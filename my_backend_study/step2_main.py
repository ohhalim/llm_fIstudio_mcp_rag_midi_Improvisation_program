from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import datetime

# 데이터 베이스 설정
DATABASE_URL = "postgresql://ohhalim@localhost:5432/my_backend_db"

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,
autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 모델(테이블 구조)
class UserDB(Base):
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
    name: str
    email: str
    age: int

    class Config:
        from_attributes = True # sqlalchemy 모델 -> pydantic 변환 허용

# Pydantic model for response
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int
    created_at: datetime

    class Config:
        from_attributes = True

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
def read_user(db: Session = Depends(get_db)):
    total_users = db.query(UserDB).count()
    return {
        "message": "PostgreSQL 연동 사용자 관리 api",
        "total_users": total_users,
        "database": "PostgreSQL 연결됨"
    }

# 모든 사용자 조회
@app.get("/users", response_model=List[User])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return users

# 특정 사용자 조회
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = 
Depends(get_db)):
    # id로 특정 사용자 조회
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, 
detail="사용자를 찾을 수 없습니다")
    return user

# 새 사용자 생성
@app.post("/users", response_model=User)
def create_user(user_data: UserCreate, db: Session =
Depends(get_db)):

    # 이메일 중복체크
    existing_user = \
db.query(UserDB).filter(UserDB.email == \
user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400,
        detail="이미 존재하는 이메일입니다")

    # 새사용자 생성
    new_user = UserDB(
        name=user_data.name,
        email=user_data.email,
        age=user_data.age
    )

    # 데이터베이스 저장
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# 사용자 삭제 
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session =
Depends(get_db)):

    # 사용자 찾기
    user = db.query(UserDB).filter(UserDB.id == 
    user_id).first()
    if not user:
        raise HTTPException(status_code=404,
    detail="사용자를 찾을 수 없습니다")

    user_name = user.name
    db.delete(user)
    db.commit()

    return {"message": f"{user_name}님 이 삭제되었습니다"}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    # sql 집계 함수 사용

    from sqlalchemy import func

    total_users = db.query(UserDB).count()

    if total_users == 0:
        return {"message": "아직 사용자가 없습니다"}

    age_stats = db.query(
        func.avg(UserDB.age).label("avg_age"),
        func.min(UserDB.age).label("min_age"),
        func.max(UserDB.age).label("max_age")
    ).first()

    users = db.query(UserDB.name).all()
    user_names = [user[0] for user in users]

    return {
        "total_users": total_users,
        "average_age": round(float(age_stats.avg_age),
        2),
        "youngest": age_stats.min_age,
        "oldest": age_stats.max_age,
        "users": user_names
    }

# 이메일로 사용자 검색
@app.get("/users/search/{email}", response_model =User)
def search_user_by_email(email: str, db: Session = 
Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == 
    email).first()

    if not user:
        raise HTTPException(status_code=404,
        detail="해당 이메일의 사용자를 찾을 수 없습니다")
    
    return user
