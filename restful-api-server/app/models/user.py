"""
사용자(User) 데이터베이스 모델
PostgreSQL 테이블과 매핑되는 SQLAlchemy 모델을 정의합니다.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    """
    사용자 테이블 모델
    
    테이블 구조:
    - id: 기본키 (자동 증가)
    - email: 이메일 (유니크, 로그인 아이디로 사용)
    - username: 사용자명 (유니크)
    - hashed_password: 암호화된 비밀번호
    - is_active: 계정 활성화 상태
    - created_at: 계정 생성 시간
    - updated_at: 계정 수정 시간
    """
    
    __tablename__ = "users"  # 실제 PostgreSQL에서 생성될 테이블명
    
    # 기본키 - 자동으로 증가하는 정수
    id = Column(Integer, primary_key=True, index=True)
    
    # 이메일 - 로그인 아이디로 사용, 중복 불가
    email = Column(String, unique=True, index=True, nullable=False)
    
    # 사용자명 - 화면에 표시될 이름, 중복 불가
    username = Column(String, unique=True, index=True, nullable=False)
    
    # 암호화된 비밀번호 - 평문 비밀번호는 절대 저장하지 않음
    hashed_password = Column(String, nullable=False)
    
    # 계정 활성화 상태 - 기본값 True
    is_active = Column(Boolean, default=True)
    
    # 계정 생성 시간 - 자동으로 현재 시간 설정
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 계정 수정 시간 - 수정될 때마다 자동으로 현재 시간으로 업데이트
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # 관계 설정: 한 사용자가 여러 게시글을 작성할 수 있음
    # back_populates를 사용해서 양방향 관계 설정
    posts = relationship("Post", back_populates="author")