from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.database import get_db
from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    Token, 
    LoginRequest,
    PasswordReset,
    PasswordResetConfirm,
    PasswordChange
)
from app.schemas.common import MessageResponse
from app.services.auth import AuthService
from app.core.security import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=Token)
async def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user and return access tokens"""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/login/oauth", response_model=Token)
async def login_oauth(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """OAuth2 compatible login endpoint"""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.authenticate_user(
            email=form_data.username,  # OAuth2 uses username field
            password=form_data.password
        )
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user (invalidate tokens)"""
    try:
        auth_service = AuthService(db)
        await auth_service.logout_user(current_user.id)
        return MessageResponse(message="Successfully logged out")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_access_token(refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(
    password_reset: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    try:
        auth_service = AuthService(db)
        await auth_service.request_password_reset(password_reset.email)
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )
    except Exception as e:
        # Always return success for security reasons
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    password_reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    try:
        auth_service = AuthService(db)
        await auth_service.confirm_password_reset(
            token=password_reset_confirm.token,
            new_password=password_reset_confirm.new_password
        )
        return MessageResponse(message="Password has been reset successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/password-change", response_model=MessageResponse)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    try:
        auth_service = AuthService(db)
        await auth_service.change_password(
            user_id=current_user.id,
            current_password=password_change.current_password,
            new_password=password_change.new_password
        )
        return MessageResponse(message="Password has been changed successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user email with token"""
    try:
        auth_service = AuthService(db)
        await auth_service.verify_email(token)
        return MessageResponse(message="Email has been verified successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_email_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend email verification"""
    try:
        auth_service = AuthService(db)
        await auth_service.resend_email_verification(current_user.id)
        return MessageResponse(message="Verification email has been sent")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )