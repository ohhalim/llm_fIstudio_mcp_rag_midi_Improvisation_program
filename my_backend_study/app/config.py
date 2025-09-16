import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "simple_app")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "user")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "password")

    @property
    def DATABASE_URL(self) -> str:
        # PostgreSQL 사용
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    # 앱 설정
    APP_NAME: str = "Simple FastAPI App"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

# 전역 설정 객체
settings = Settings()