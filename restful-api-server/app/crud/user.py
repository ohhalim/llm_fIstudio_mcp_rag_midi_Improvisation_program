"""
사용자 관련 CRUD (Create, Read, Update, Delete) 작업
데이터베이스와 직접 상호작용하는 함수들을 정의합니다.
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    ID로 사용자 조회
    
    Args:
        db: 데이터베이스 세션
        user_id: 조회할 사용자 ID
    
    Returns:
        User 객체 또는 None (사용자가 없는 경우)
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    이메일로 사용자 조회
    로그인 시 사용자 확인용
    
    Args:
        db: 데이터베이스 세션
        email: 조회할 이메일
    
    Returns:
        User 객체 또는 None
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    사용자명으로 사용자 조회
    중복 검사용
    """
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    새 사용자 생성 (회원가입)
    
    Args:
        db: 데이터베이스 세션
        user: 사용자 생성 정보
    
    Returns:
        생성된 User 객체
    """
    # 비밀번호 해싱 (평문 비밀번호는 절대 저장하지 않음!)
    hashed_password = get_password_hash(user.password)
    
    # User 객체 생성
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    # 데이터베이스에 추가
    db.add(db_user)
    db.commit()  # 변경사항 저장
    db.refresh(db_user)  # 생성된 ID 등을 다시 로드
    
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    사용자 인증 (로그인)
    이메일과 비밀번호로 사용자 확인
    
    Args:
        db: 데이터베이스 세션
        email: 로그인 이메일
        password: 로그인 비밀번호 (평문)
    
    Returns:
        인증된 User 객체 또는 None (인증 실패)
    """
    # 이메일로 사용자 찾기
    user = get_user_by_email(db, email)
    
    # 사용자가 없거나 비밀번호가 틀린 경우
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    # 계정이 비활성화된 경우
    if not user.is_active:
        return None
        
    return user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    사용자 정보 수정
    
    Args:
        db: 데이터베이스 세션
        user_id: 수정할 사용자 ID
        user_update: 수정할 정보
    
    Returns:
        수정된 User 객체 또는 None (사용자가 없는 경우)
    """
    # 기존 사용자 조회
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    # 수정할 필드만 업데이트
    update_data = user_update.dict(exclude_unset=True)  # None이 아닌 필드만
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """
    사용자 삭제 (실제로는 비활성화)
    
    Args:
        db: 데이터베이스 세션
        user_id: 삭제할 사용자 ID
    
    Returns:
        삭제 성공 여부
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    # 실제 삭제 대신 비활성화 (데이터 보존)
    user.is_active = False
    db.commit()
    
    return True