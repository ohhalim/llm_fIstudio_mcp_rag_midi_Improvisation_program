"""
게시글 관련 Pydantic 스키마
게시판 API의 요청/응답 데이터 구조를 정의합니다.
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from .user import UserResponse

class PostBase(BaseModel):
    """
    게시글의 기본 정보 스키마
    """
    title: str
    content: str

class PostCreate(PostBase):
    """
    게시글 생성 요청 스키마
    클라이언트에서 새 게시글을 작성할 때 사용
    """
    @validator('title')
    def validate_title(cls, v):
        """제목 유효성 검사"""
        if not v or len(v.strip()) < 1:
            raise ValueError('제목은 필수입니다.')
        if len(v) > 200:
            raise ValueError('제목은 200자를 초과할 수 없습니다.')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        """내용 유효성 검사"""
        if not v or len(v.strip()) < 1:
            raise ValueError('내용은 필수입니다.')
        return v.strip()

class PostUpdate(BaseModel):
    """
    게시글 수정 요청 스키마
    수정 가능한 필드만 포함, 모든 필드는 선택사항
    """
    title: Optional[str] = None
    content: Optional[str] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError('제목은 비워둘 수 없습니다.')
            if len(v) > 200:
                raise ValueError('제목은 200자를 초과할 수 없습니다.')
            return v.strip()
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError('내용은 비워둘 수 없습니다.')
            return v.strip()
        return v

class PostResponse(PostBase):
    """
    게시글 정보 응답 스키마
    API에서 게시글 정보를 반환할 때 사용
    """
    id: int
    author_id: int
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # 작성자 정보도 함께 포함
    author: UserResponse
    
    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    """
    게시글 목록 응답 스키마
    페이징 정보와 함께 게시글 목록을 반환
    """
    posts: List[PostResponse]
    total: int  # 전체 게시글 수
    page: int   # 현재 페이지
    size: int   # 페이지 크기
    total_pages: int  # 전체 페이지 수