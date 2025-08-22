"""
게시글(Post) 데이터베이스 모델
게시판 기능을 위한 테이블 모델을 정의합니다.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Post(Base):
    """
    게시글 테이블 모델
    
    테이블 구조:
    - id: 기본키 (자동 증가)
    - title: 게시글 제목
    - content: 게시글 내용 (긴 텍스트)
    - author_id: 작성자 ID (users 테이블의 외래키)
    - file_path: 업로드된 파일 경로 (선택사항)
    - created_at: 게시글 작성 시간
    - updated_at: 게시글 수정 시간
    """
    
    __tablename__ = "posts"  # PostgreSQL 테이블명
    
    # 기본키 - 게시글 고유 번호
    id = Column(Integer, primary_key=True, index=True)
    
    # 게시글 제목 - 필수 입력, 검색에 사용되므로 인덱스 추가
    title = Column(String(200), nullable=False, index=True)
    
    # 게시글 내용 - 긴 텍스트를 위해 Text 타입 사용
    content = Column(Text, nullable=False)
    
    # 작성자 ID - users 테이블의 id를 참조하는 외래키
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 업로드된 파일 경로 - 파일이 없을 수도 있으므로 nullable=True
    file_path = Column(String(500), nullable=True)
    
    # 게시글 작성 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 게시글 수정 시간
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # 관계 설정: 게시글 작성자 정보를 가져올 수 있음
    # back_populates를 통해 User 모델과 양방향 관계 설정
    author = relationship("User", back_populates="posts")