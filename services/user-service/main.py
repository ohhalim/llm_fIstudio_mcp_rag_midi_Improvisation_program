from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import sys
import os

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.config import get_settings
from shared.database import init_database, get_db
from shared.auth import init_auth
from shared.logging import setup_logging, get_logger, logging_middleware

from .models import User
from .schemas import (
    UserCreate, UserUpdate, UserPasswordUpdate, UserLogin,
    Token, UserResponse, UsersListResponse, MessageResponse
)
from .crud import UserCRUD

# 설정 초기화
settings = get_settings("user-service", 8001)
setup_logging("user-service")
logger = get_logger(__name__)

# 데이터베이스 및 인증 초기화
db_manager = init_database(settings.db)
auth_manager = init_auth(settings.auth)
user_crud = UserCRUD(auth_manager)

app = FastAPI(
    title="User Service",
    description="사용자 관리 마이크로서비스",
    version="1.0.0"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 미들웨어
app.middleware("http")(logging_middleware)

security = HTTPBearer(auto_error=False)

@app.on_event("startup")
async def startup_event():
    await db_manager.create_tables()
    logger.info("User Service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("User Service shutting down")

# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

# 인증 엔드포인트
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """사용자 등록"""
    try:
        db_user = user_crud.create_user(db, user)
        return UserResponse(user=db_user, message="User created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인"""
    user = user_crud.authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    access_token = auth_manager.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.auth.access_token_expire_minutes * 60
    )

# 헤더에서 현재 사용자 정보 추출 (Gateway에서 전달)
def get_current_user_from_header(request):
    user_id = request.headers.get("X-User-ID")
    user_email = request.headers.get("X-User-Email")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {"sub": int(user_id), "email": user_email}

# 사용자 프로필 엔드포인트
@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_profile(request, db: Session = Depends(get_db)):
    """현재 사용자 프로필 조회"""
    user_info = get_current_user_from_header(request)
    user = user_crud.get_user_by_id(db, user_info["sub"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(user=user)

@app.put("/api/users/me", response_model=UserResponse)
async def update_current_user_profile(
    request,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """현재 사용자 프로필 업데이트"""
    user_info = get_current_user_from_header(request)
    
    try:
        updated_user = user_crud.update_user(db, user_info["sub"], user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(user=updated_user, message="Profile updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/users/me/password", response_model=MessageResponse)
async def update_password(
    request,
    password_update: UserPasswordUpdate,
    db: Session = Depends(get_db)
):
    """비밀번호 변경"""
    user_info = get_current_user_from_header(request)
    
    success = user_crud.update_password(
        db, 
        user_info["sub"], 
        password_update.current_password, 
        password_update.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    return MessageResponse(message="Password updated successfully")

# 사용자 관리 엔드포인트 (관리자용)
@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """특정 사용자 조회"""
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(user=user)

@app.get("/api/users", response_model=UsersListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """사용자 목록 조회"""
    users = user_crud.get_users(db, skip=skip, limit=limit)
    total = user_crud.get_users_count(db)
    
    return UsersListResponse(
        users=users,
        total=total,
        page=skip // limit + 1,
        size=len(users)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.service.service_host,
        port=settings.service.service_port,
        reload=settings.service.debug,
        log_config=None
    )