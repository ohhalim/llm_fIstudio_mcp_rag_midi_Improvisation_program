from sqlalchemy.orm import Session
from .model import User
from .schemas import UserCreate, UserUpdate

def get_user(db: Session, user_id: int):
    """ID로 사용자 조회"""
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    """사용자 목록 조회"""
    return db.query(User).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, email: str):
    """이메일로 사용자 조회"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """사용자 생성"""
    db_user = User(**user.dict()) # pydantic -> sqlalchemy 변환
    db.add(db_user) # 메모리에 추가
    db.commit() # db에 저장
    db.refresh(db_user) # 새로 생성된 필드 가져오기
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """사용자 정보 업데이트"""
    db_user = get_user(db, user_id)
    if db_user:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """사용자 삭제"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False