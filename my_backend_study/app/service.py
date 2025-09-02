from sqlalchemy.orm import Session
from typing import List, Optional
from .repository import UserRepository
from .schemas import UserCreate, UserUpdate, UserResponse

class UserService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository
    
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """사용자 조회 서비스"""
        user = self.repository.get_user_by_id(self.db, user_id)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """이메일로 사용자 조회 서비스"""
        user = self.repository.get_user_by_email(self.db, email)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def get_all_users(self) -> List[UserResponse]:
        """모든 사용자 조회 서비스"""
        users = self.repository.get_all_users(self.db)
        return [UserResponse.from_orm(user) for user in users]
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """사용자 생성 서비스"""
        # 이메일 중복 체크
        if self.repository.get_user_by_email(self.db, user_data.email):
            raise ValueError("User with this email already exists")
        
        user = self.repository.create_user(self.db, user_data)
        return UserResponse.from_orm(user)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """사용자 업데이트 서비스"""
        # 이메일 중복 체크 (이메일을 변경하는 경우)
        if user_data.email:
            existing_user = self.repository.get_user_by_email(self.db, user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("User with this email already exists")
        
        user = self.repository.update_user(self.db, user_id, user_data)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def delete_user(self, user_id: int) -> bool:
        """사용자 삭제 서비스"""
        return self.repository.delete_user(self.db, user_id)
