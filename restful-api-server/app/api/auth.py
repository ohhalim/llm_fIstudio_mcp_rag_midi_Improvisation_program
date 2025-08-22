"""
인증 관련 API 엔드포인트
회원가입, 로그인 등의 인증 기능을 제공합니다.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.crud.user import create_user, authenticate_user, get_user_by_email, get_user_by_username
from app.core.security import create_access_token
from app.core.config import settings
from app.core.deps import get_current_user

# 인증 관련 라우터 생성
router = APIRouter(
    prefix="/auth",  # 모든 엔드포인트 앞에 /auth가 붙음
    tags=["인증"]     # Swagger 문서에서 그룹화할 때 사용
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    회원가입 엔드포인트
    
    새로운 사용자 계정을 생성합니다.
    이메일과 사용자명은 중복될 수 없습니다.
    
    Args:
        user: 회원가입 정보 (이메일, 사용자명, 비밀번호)
        db: 데이터베이스 세션
    
    Returns:
        UserResponse: 생성된 사용자 정보 (비밀번호 제외)
    
    Raises:
        HTTPException: 이메일 또는 사용자명이 이미 존재할 때
    """
    
    # 이메일 중복 검사
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 사용자명 중복 검사
    existing_username = get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다."
        )
    
    # 새 사용자 생성
    db_user = create_user(db, user)
    return db_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    로그인 엔드포인트
    
    이메일과 비밀번호로 로그인하고 JWT 토큰을 발급합니다.
    
    Args:
        user_credentials: 로그인 정보 (이메일, 비밀번호)
        db: 데이터베이스 세션
    
    Returns:
        Token: JWT 액세스 토큰과 토큰 타입
    
    Raises:
        HTTPException: 로그인 정보가 올바르지 않을 때
    """
    
    # 사용자 인증 (이메일과 비밀번호 확인)
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # JWT 토큰 생성
    # 토큰 만료 시간 설정
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    
    # 토큰에 포함할 데이터 (subject에 이메일을 저장)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회 엔드포인트
    
    JWT 토큰을 통해 현재 로그인한 사용자의 정보를 반환합니다.
    토큰이 유효하지 않으면 401 에러를 반환합니다.
    
    사용법:
    Authorization: Bearer <your-jwt-token>
    
    Args:
        current_user: 현재 로그인한 사용자 (의존성 주입으로 자동 제공)
    
    Returns:
        UserResponse: 현재 사용자 정보
    """
    return current_user

# 추가적인 인증 관련 엔드포인트들을 여기에 추가할 수 있습니다.
# 예: 비밀번호 변경, 토큰 새로고침, 로그아웃 등