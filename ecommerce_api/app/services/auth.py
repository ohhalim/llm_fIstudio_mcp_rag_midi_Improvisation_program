from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, Token
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_refresh_token,
    create_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            password_hash=hashed_password,
            role=user_data.role,
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    async def authenticate_user(self, email: str, password: str) -> Token:
        """Authenticate user and return tokens"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Incorrect email or password")
        
        if not user.is_active:
            raise ValueError("User account is disabled")
        
        # Update last login
        user.last_login = func.now()
        self.db.commit()
        
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        token_data = verify_refresh_token(refresh_token)
        
        if not token_data:
            raise ValueError("Invalid refresh token")
        
        user = self.db.query(User).filter(User.id == token_data.user_id).first()
        
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Create new tokens
        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    async def logout_user(self, user_id: int) -> bool:
        """Logout user (in a full implementation, this would invalidate tokens)"""
        # In a full implementation, you would add token blacklisting here
        # For now, we just return True as the client will remove the tokens
        return True

    async def request_password_reset(self, email: str) -> bool:
        """Request password reset"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if user exists for security
            return True
        
        # Create password reset token
        reset_token = create_password_reset_token(user.id)
        
        # In a full implementation, you would send this token via email
        # For now, we'll just store it (you could add a table for this)
        print(f"Password reset token for {email}: {reset_token}")
        
        return True

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset with token"""
        user_id = verify_password_reset_token(token)
        
        if not user_id:
            raise ValueError("Invalid or expired reset token")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        return True

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        return True

    async def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        user_id = verify_email_verification_token(token)
        
        if not user_id:
            raise ValueError("Invalid or expired verification token")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Mark email as verified (you might want to add this field to User model)
        # user.email_verified = True
        self.db.commit()
        
        return True

    async def resend_email_verification(self, user_id: int) -> bool:
        """Resend email verification"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Create verification token
        verification_token = create_email_verification_token(user.id)
        
        # In a full implementation, you would send this token via email
        print(f"Email verification token for {user.email}: {verification_token}")
        
        return True