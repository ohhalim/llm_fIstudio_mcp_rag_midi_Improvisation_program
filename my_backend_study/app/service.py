from sqlalchemy.orm import Session
from fastapi import HTTPException
from .repository import (
    get_user, get_users, get_user_by_email, 
    create_user, update_user, delete_user
)
from .schemas import UserCreate, UserUpdate, UserResponse

class UserService:
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> UserResponse:
        """ID로 사용자 조회"""
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10):
        """모든 사용자 조회"""
        return get_users(db, skip, limit)
    
    @staticmethod
    def create_new_user(db: Session, user: UserCreate) -> UserResponse:
        """새 사용자 생성"""
        # 이메일 중복 체크
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        return create_user(db, user)
    
    @staticmethod
    def update_existing_user(db: Session, user_id: int, user_update: UserUpdate) -> UserResponse:
        """사용자 정보 업데이트"""
        user = update_user(db, user_id, user_update)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def delete_existing_user(db: Session, user_id: int):
        """사용자 삭제"""
        if not delete_user(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}