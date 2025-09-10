import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = Field(default="E-commerce API", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=True, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db",
        env="DATABASE_URL"
    )
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="your-super-secret-jwt-key-change-this-in-production",
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Security Settings
    SECRET_KEY: str = Field(
        default="your-super-secret-app-key-change-this-in-production",
        env="SECRET_KEY"
    )
    BCRYPT_ROUNDS: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    # Payment Configuration (Stripe)
    STRIPE_PUBLISHABLE_KEY: str = Field(default="", env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY: str = Field(default="", env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")
    
    # File Upload Settings
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "pdf"]
    
    # Email Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    FROM_EMAIL: str = Field(default="noreply@yourstore.com", env="FROM_EMAIL")
    
    # Frontend URL (for CORS)
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    
    # Admin Configuration
    ADMIN_EMAIL: str = Field(default="admin@yourstore.com", env="ADMIN_EMAIL")
    ADMIN_PASSWORD: str = Field(default="admin123", env="ADMIN_PASSWORD")
    
    # Token Configuration
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES")
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, env="EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES")  # 24 hours
    
    # API Configuration
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()