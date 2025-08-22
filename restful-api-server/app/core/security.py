"""
보안 관련 유틸리티 모듈
JWT 토큰 생성/검증, 비밀번호 해싱 등을 처리합니다.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

# 비밀번호 해싱을 위한 컨텍스트 생성
# bcrypt 알고리즘 사용 (가장 안전하고 널리 사용됨)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교
    
    Args:
        plain_password: 사용자가 입력한 평문 비밀번호
        hashed_password: 데이터베이스에 저장된 해시된 비밀번호
    
    Returns:
        bool: 비밀번호가 일치하면 True, 아니면 False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    평문 비밀번호를 해시화
    
    Args:
        password: 해시화할 평문 비밀번호
    
    Returns:
        str: 해시화된 비밀번호
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성
    
    Args:
        data: 토큰에 포함할 데이터 (보통 사용자 정보)
        expires_delta: 토큰 만료 시간 (None이면 기본값 사용)
    
    Returns:
        str: 생성된 JWT 토큰
    """
    # 토큰에 포함할 데이터 복사
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 기본 만료 시간은 설정에서 가져옴
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    # 만료 시간을 토큰 데이터에 추가
    to_encode.update({"exp": expire})
    
    # JWT 토큰 생성 및 반환
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    JWT 토큰 검증 및 이메일 추출
    
    Args:
        token: 검증할 JWT 토큰
    
    Returns:
        Optional[str]: 토큰이 유효하면 이메일, 아니면 None
    
    Raises:
        HTTPException: 토큰이 유효하지 않을 때
    """
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # 토큰에서 이메일 추출
        email: str = payload.get("sub")
        
        # 이메일이 없으면 유효하지 않은 토큰
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에서 사용자 정보를 찾을 수 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return email
        
    except JWTError:
        # JWT 디코딩 실패 시
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )