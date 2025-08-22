"""
게시판 관련 API 엔드포인트
게시글의 CRUD 기능을 제공합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import math

from app.db.database import get_db
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from app.crud import post as post_crud
from app.core.deps import get_current_active_user
from app.models.user import User

# 게시판 관련 라우터 생성
router = APIRouter(
    prefix="/posts",  # 모든 엔드포인트 앞에 /posts가 붙음
    tags=["게시판"]    # Swagger 문서에서 그룹화
)

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    새 게시글 작성
    
    로그인한 사용자만 게시글을 작성할 수 있습니다.
    JWT 토큰이 필요합니다.
    
    Args:
        post: 게시글 작성 정보 (제목, 내용)
        db: 데이터베이스 세션
        current_user: 현재 로그인한 사용자
    
    Returns:
        PostResponse: 생성된 게시글 정보
    """
    return post_crud.create_post(db=db, post=post, author_id=current_user.id)

@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    size: int = Query(10, ge=1, le=100, description="페이지당 게시글 수 (최대 100개)"),
    search: Optional[str] = Query(None, description="검색어 (제목, 내용에서 검색)"),
    db: Session = Depends(get_db)
):
    """
    게시글 목록 조회 (페이징 및 검색)
    
    모든 사용자가 접근 가능합니다. (로그인 불필요)
    페이징과 검색 기능을 제공합니다.
    
    Args:
        page: 페이지 번호 (기본값: 1)
        size: 페이지당 게시글 수 (기본값: 10, 최대: 100)
        search: 검색어 (선택사항)
        db: 데이터베이스 세션
    
    Returns:
        PostListResponse: 게시글 목록과 페이징 정보
    """
    # skip 계산: (페이지 번호 - 1) * 페이지 크기
    skip = (page - 1) * size
    
    # 게시글 목록과 전체 수 조회
    posts, total = post_crud.get_posts(db=db, skip=skip, limit=size, search=search)
    
    # 전체 페이지 수 계산
    total_pages = math.ceil(total / size) if total > 0 else 1
    
    return PostListResponse(
        posts=posts,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    특정 게시글 조회
    
    게시글 ID로 하나의 게시글을 조회합니다.
    모든 사용자가 접근 가능합니다.
    
    Args:
        post_id: 조회할 게시글 ID
        db: 데이터베이스 세션
    
    Returns:
        PostResponse: 게시글 정보
    
    Raises:
        HTTPException: 게시글을 찾을 수 없을 때 (404)
    """
    post = post_crud.get_post_by_id(db=db, post_id=post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )
    
    return post

@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글 수정
    
    본인이 작성한 게시글만 수정할 수 있습니다.
    JWT 토큰이 필요합니다.
    
    Args:
        post_id: 수정할 게시글 ID
        post_update: 수정할 내용
        db: 데이터베이스 세션
        current_user: 현재 로그인한 사용자
    
    Returns:
        PostResponse: 수정된 게시글 정보
    
    Raises:
        HTTPException: 게시글이 없거나 수정 권한이 없을 때
    """
    post = post_crud.update_post(
        db=db, 
        post_id=post_id, 
        post_update=post_update, 
        user_id=current_user.id
    )
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없거나 수정 권한이 없습니다."
        )
    
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글 삭제
    
    본인이 작성한 게시글만 삭제할 수 있습니다.
    JWT 토큰이 필요합니다.
    
    Args:
        post_id: 삭제할 게시글 ID
        db: 데이터베이스 세션
        current_user: 현재 로그인한 사용자
    
    Returns:
        None: 성공 시 204 No Content 반환
    
    Raises:
        HTTPException: 게시글이 없거나 삭제 권한이 없을 때
    """
    success = post_crud.delete_post(
        db=db, 
        post_id=post_id, 
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없거나 삭제 권한이 없습니다."
        )

@router.get("/users/{user_id}", response_model=PostListResponse)
def get_posts_by_user(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    특정 사용자가 작성한 게시글 목록 조회
    
    Args:
        user_id: 조회할 사용자 ID
        page: 페이지 번호
        size: 페이지당 게시글 수
        db: 데이터베이스 세션
    
    Returns:
        PostListResponse: 해당 사용자의 게시글 목록
    """
    skip = (page - 1) * size
    posts, total = post_crud.get_posts_by_author(db=db, author_id=user_id, skip=skip, limit=size)
    
    total_pages = math.ceil(total / size) if total > 0 else 1
    
    return PostListResponse(
        posts=posts,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )