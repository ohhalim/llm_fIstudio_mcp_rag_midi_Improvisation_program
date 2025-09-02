# 환경변수에 접근하기 위해 사용
import os
# 설정값을 검증하고 관리하는 pydantic 베이스클래스
from pydantic_settings import BaseSettings

# 에플리캐이션 설정담당
class Settings(BaseSettings):

    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    # 문자열을 정수로 변환
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "fastapi_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "password")

    # 앱이름
    APP_NAME: str = "FastAPI CRUD App"
    # 디버그 모드 설정 (환경 변수에서 문자열을 불리언으로 변환)
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # 데코레이터로 계산된 속성 생성
    @property
    # db 연결 URL을 동적으로 생성
    def database_url(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

settings = Settings()
