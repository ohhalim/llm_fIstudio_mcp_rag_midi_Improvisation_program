"""
설정 관리 모듈
환경변수를 읽어와서 애플리케이션 전반에서 사용할 설정값들을 관리합니다.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    .env 파일이나 환경변수에서 값을 자동으로 읽어옵니다.
    """
    
    # 데이터베이스 설정
    database_url: str = "postgresql://username:password@localhost:5432/restful_api_db"
    
    # JWT 토큰 설정
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # 파일 업로드 설정
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    # CORS 설정 (프론트엔드와 연결할 때 필요)
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        # .env 파일에서 설정값을 읽어옴
        env_file = ".env"

# 전역에서 사용할 설정 인스턴스 생성
settings = Settings()