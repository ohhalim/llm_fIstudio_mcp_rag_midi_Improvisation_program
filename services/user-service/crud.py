from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import json
from datetime import datetime

from .models import User, UserSession
from .schemas import UserCreate, UserUpdate
import sys
import os

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.auth import AuthManager

class UserCRUD:
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        return db.query(User).filter(User.username == username).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """사용자 목록 조회"""
        return db.query(User).offset(skip).limit(limit).all()
    
    def get_users_count(self, db: Session) -> int:
        """총 사용자 수 조회"""
        return db.query(func.count(User.id)).scalar()
    
    def create_user(self, db: Session, user: UserCreate) -> User:
        """사용자 생성"""
        # 중복 체크
        if self.get_user_by_email(db, user.email):
            raise ValueError("Email already registered")
        if self.get_user_by_username(db, user.username):
            raise ValueError("Username already taken")
        
        # 비밀번호 해시화
        hashed_password = self.auth_manager.get_password_hash(user.password)
        
        # JSON 직렬화
        preferred_instruments = json.dumps(user.preferred_instruments) if user.preferred_instruments else None
        music_style_preferences = json.dumps(user.music_style_preferences) if user.music_style_preferences else None
        
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            preferred_instruments=preferred_instruments,
            music_style_preferences=music_style_preferences
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # JSON 역직렬화하여 반환
        if db_user.preferred_instruments:
            db_user.preferred_instruments = json.loads(db_user.preferred_instruments)
        if db_user.music_style_preferences:
            db_user.music_style_preferences = json.loads(db_user.music_style_preferences)
        
        return db_user
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """사용자 정보 업데이트"""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # 중복 체크
        if "email" in update_data and update_data["email"] != db_user.email:
            if self.get_user_by_email(db, update_data["email"]):
                raise ValueError("Email already registered")
        
        if "username" in update_data and update_data["username"] != db_user.username:
            if self.get_user_by_username(db, update_data["username"]):
                raise ValueError("Username already taken")
        
        # JSON 직렬화
        if "preferred_instruments" in update_data:
            update_data["preferred_instruments"] = json.dumps(update_data["preferred_instruments"])
        if "music_style_preferences" in update_data:
            update_data["music_style_preferences"] = json.dumps(update_data["music_style_preferences"])
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        # JSON 역직렬화하여 반환
        if db_user.preferred_instruments:
            db_user.preferred_instruments = json.loads(db_user.preferred_instruments)
        if db_user.music_style_preferences:
            db_user.music_style_preferences = json.loads(db_user.music_style_preferences)
        
        return db_user
    
    def update_password(self, db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """비밀번호 변경"""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        # 현재 비밀번호 확인
        if not self.auth_manager.verify_password(current_password, db_user.hashed_password):
            return False
        
        # 새 비밀번호 해시화 및 저장
        db_user.hashed_password = self.auth_manager.get_password_hash(new_password)
        db.commit()
        
        return True
    
    def update_last_login(self, db: Session, user_id: int) -> None:
        """마지막 로그인 시간 업데이트"""
        db_user = self.get_user_by_id(db, user_id)
        if db_user:
            db_user.last_login = datetime.utcnow()
            db.commit()
    
    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """사용자 비활성화"""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        db.commit()
        return True
    
    def activate_user(self, db: Session, user_id: int) -> bool:
        """사용자 활성화"""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db_user.is_active = True
        db.commit()
        return True
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """사용자 인증"""
        user = self.get_user_by_email(db, email)
        if not user:
            return None
        if not self.auth_manager.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        
        # 마지막 로그인 시간 업데이트
        self.update_last_login(db, user.id)
        
        # JSON 역직렬화
        if user.preferred_instruments:
            user.preferred_instruments = json.loads(user.preferred_instruments)
        if user.music_style_preferences:
            user.music_style_preferences = json.loads(user.music_style_preferences)
        
        return user