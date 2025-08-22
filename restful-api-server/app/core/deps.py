"""
의존성 주입 모듈
FastAPI의 Dependency Injection 시스템에서 사용할 의존성 함수들을 정의합니다.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import verify_token
from app.crud.user import get_user_by_email
from app.models.user import User

# HTTPBearer 스키마 설정 - Authorization 헤더에서 Bearer 토큰을 자동으로 추출
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 로그인한 사용자를 가져오는 의존성 함수
    
    JWT 토큰을 검증하고 해당하는 사용자 정보를 반환합니다.
    인증이 필요한 모든 엔드포인트에서 사용됩니다.
    
    사용법:
    @app.get("/protected-endpoint")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"message": f"안녕하세요, {current_user.username}님!"}
    
    Args:
        credentials: HTTP Bearer 토큰 (자동으로 추출됨)
        db: 데이터베이스 세션
    
    Returns:
        User: 현재 로그인한 사용자 객체
    
    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없을 때
    """
    
    # JWT 토큰에서 이메일 추출 및 검증
    email = verify_token(credentials.credentials)
    
    # 이메일로 사용자 조회
    user = get_user_by_email(db, email)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 계정이 비활성화된 경우
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    활성화된 사용자만 허용하는 의존성 함수
    
    이미 get_current_user에서 활성화 검사를 하므로 
    실제로는 같은 역할을 하지만, 명시적으로 활성화된 사용자만 
    받겠다는 의미를 표현할 때 사용
    
    Args:
        current_user: 현재 사용자
    
    Returns:
        User: 활성화된 사용자 객체
    """
    return current_user