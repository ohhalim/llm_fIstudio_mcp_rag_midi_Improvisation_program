import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:qwe123@db:5432/mydb")
    
    # 앱 설정
    APP_NAME: str = "Simple FastAPI App"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

# 전역 설정 객체
settings = Settings()