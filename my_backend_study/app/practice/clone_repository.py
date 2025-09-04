from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List,Optional
from .model import User
from .schemas import UserCreate, UserUpdate

class UserRepository:

    @staticmethod
    def get_user_by_id(db: Session, user_id:int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session,email: str ) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def det_all_users(db: Session) -> List[User]:
        return db.query(User).all()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """새 사용자 생성"""
        try:
            db_user = User(
                name=user_data.name,
                email=user_data.email,
                age=user_data.age,
                is_active=user_data.is_active
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already exists")
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """사용자 정보 업데이트"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
            
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already exists")
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """사용자 삭제"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
            
        db.delete(db_user)
        db.commit()
        return True
