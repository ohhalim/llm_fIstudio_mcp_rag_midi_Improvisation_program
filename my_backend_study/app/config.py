import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "fastapi_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "password")
    
    # 애플리케이션 설정
    APP_NAME: str = "FastAPI CRUD App"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

# 전역 설정 객체 생성
settings = Settings()
