"""
게시글 관련 CRUD 작업
게시판의 생성, 조회, 수정, 삭제 기능을 구현합니다.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from typing import List, Optional
import math

def create_post(db: Session, post: PostCreate, author_id: int, file_path: Optional[str] = None) -> Post:
    """
    새 게시글 생성
    
    Args:
        db: 데이터베이스 세션
        post: 게시글 생성 정보
        author_id: 작성자 ID
        file_path: 업로드된 파일 경로 (선택사항)
    
    Returns:
        Post: 생성된 게시글 객체
    """
    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=author_id,
        file_path=file_path
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post

def get_post_by_id(db: Session, post_id: int) -> Optional[Post]:
    """
    ID로 게시글 조회 (작성자 정보 포함)
    
    Args:
        db: 데이터베이스 세션
        post_id: 조회할 게시글 ID
    
    Returns:
        Post: 게시글 객체 (작성자 정보 포함) 또는 None
    """
    return db.query(Post).options(
        joinedload(Post.author)  # 작성자 정보도 함께 로드 (N+1 쿼리 방지)
    ).filter(Post.id == post_id).first()

def get_posts(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = None
) -> tuple[List[Post], int]:
    """
    게시글 목록 조회 (페이징 및 검색 포함)
    
    Args:
        db: 데이터베이스 세션
        skip: 건너뛸 게시글 수 (페이징용)
        limit: 한 페이지당 게시글 수
        search: 검색어 (제목이나 내용에서 검색)
    
    Returns:
        tuple[List[Post], int]: (게시글 목록, 전체 게시글 수)
    """
    # 기본 쿼리 (작성자 정보 포함, 최신순 정렬)
    query = db.query(Post).options(
        joinedload(Post.author)
    ).order_by(desc(Post.created_at))
    
    # 검색어가 있는 경우 필터 적용
    if search:
        # 제목이나 내용에 검색어가 포함된 게시글 찾기
        search_filter = or_(
            Post.title.ilike(f"%{search}%"),    # 대소문자 무시하고 검색
            Post.content.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # 전체 게시글 수 계산 (페이징 정보용)
    total = query.count()
    
    # 페이징 적용하여 게시글 목록 조회
    posts = query.offset(skip).limit(limit).all()
    
    return posts, total

def update_post(db: Session, post_id: int, post_update: PostUpdate, user_id: int) -> Optional[Post]:
    """
    게시글 수정
    
    Args:
        db: 데이터베이스 세션
        post_id: 수정할 게시글 ID
        post_update: 수정할 내용
        user_id: 수정 요청한 사용자 ID (작성자 확인용)
    
    Returns:
        Post: 수정된 게시글 객체 또는 None (게시글이 없거나 권한이 없는 경우)
    """
    # 게시글 조회
    post = get_post_by_id(db, post_id)
    if not post:
        return None
    
    # 작성자 확인 (본인만 수정 가능)
    if post.author_id != user_id:
        return None
    
    # 수정할 필드만 업데이트
    update_data = post_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    return post

def delete_post(db: Session, post_id: int, user_id: int) -> bool:
    """
    게시글 삭제
    
    Args:
        db: 데이터베이스 세션
        post_id: 삭제할 게시글 ID
        user_id: 삭제 요청한 사용자 ID (작성자 확인용)
    
    Returns:
        bool: 삭제 성공 여부
    """
    # 게시글 조회
    post = get_post_by_id(db, post_id)
    if not post:
        return False
    
    # 작성자 확인 (본인만 삭제 가능)
    if post.author_id != user_id:
        return False
    
    # 게시글 삭제
    db.delete(post)
    db.commit()
    
    return True

def get_posts_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 10) -> tuple[List[Post], int]:
    """
    특정 사용자가 작성한 게시글 목록 조회
    
    Args:
        db: 데이터베이스 세션
        author_id: 작성자 ID
        skip: 건너뛸 게시글 수
        limit: 한 페이지당 게시글 수
    
    Returns:
        tuple[List[Post], int]: (게시글 목록, 전체 게시글 수)
    """
    query = db.query(Post).options(
        joinedload(Post.author)
    ).filter(Post.author_id == author_id).order_by(desc(Post.created_at))
    
    total = query.count()
    posts = query.offset(skip).limit(limit).all()
    
    return posts, total