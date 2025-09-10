from sqlalchemy.orm import Session
from .simple_model import User
from .simple_schemas import UserCreate, UserUpdate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def get_user_by_email(db:Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db:Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        for field, value in user_update.dict(exclude_unset=true).items():
            setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
    return db_user

def delete_user(db:Session, user_id: int):
    db_user =get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

