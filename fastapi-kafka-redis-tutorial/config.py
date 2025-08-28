"""
config.py - 애플리케이션 설정 파일

이 파일에서 배울 수 있는 개념들:
1. Pydantic Settings: 환경변수를 자동으로 읽어오는 방법
2. 설정 중앙화: 모든 설정을 한 곳에서 관리
3. 타입 힌팅: 설정값의 타입을 명시하여 안전성 확보
4. 기본값 설정: 환경변수가 없을 때의 기본값 제공
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    
    BaseSettings를 상속받으면 환경변수를 자동으로 매핑해줍니다.
    예: REDIS_URL 환경변수가 있으면 redis_url 필드에 자동 할당
    """
    
    # Redis 설정
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0  # Redis 데이터베이스 번호 (0~15)
    redis_max_connections: int = 10  # 최대 연결 수
    
    # Kafka 설정
    kafka_bootstrap_servers: str = "localhost:9092"  # Kafka 브로커 주소
    kafka_group_id: str = "fastapi_group"  # 컨슈머 그룹 ID
    kafka_auto_offset_reset: str = "latest"  # 오프셋 리셋 정책 (earliest/latest)
    
    # 애플리케이션 설정
    app_name: str = "FastAPI Kafka Redis Tutorial"
    app_version: str = "1.0.0"
    debug: bool = True  # 디버그 모드
    
    # PostgreSQL 데이터베이스 설정
    database_url: str = "postgresql+asyncpg://tutorial_user:tutorial_password@localhost:5432/fastapi_tutorial"
    database_sync_url: str = "postgresql://tutorial_user:tutorial_password@localhost:5432/fastapi_tutorial"
    
    # 데이터베이스 연결 풀 설정
    db_pool_size: int = 20
    db_max_overflow: int = 0
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    
    # JWT 및 보안 설정
    secret_key: str = "your-super-secret-key-change-this-in-production-must-be-at-least-32-characters"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 비밀번호 해싱 설정
    password_hash_rounds: int = 12
    
    class Config:
        """
        Pydantic 설정 클래스
        """
        env_file = ".env"  # .env 파일에서 환경변수 읽기
        case_sensitive = False  # 대소문자 구분 안함


# 싱글톤 패턴: 애플리케이션 전체에서 하나의 설정 인스턴스만 사용
settings = Settings()

# 설정 정보 출력 함수 (디버깅용)
def print_settings():
    """
    현재 설정 정보를 출력하는 디버깅 함수
    """
    print("=" * 50)
    print("현재 애플리케이션 설정:")
    print(f"앱 이름: {settings.app_name}")
    print(f"앱 버전: {settings.app_version}")
    print(f"디버그 모드: {settings.debug}")
    print(f"Redis URL: {settings.redis_url}")
    print(f"Kafka 서버: {settings.kafka_bootstrap_servers}")
    print(f"Kafka 그룹 ID: {settings.kafka_group_id}")
    print("=" * 50)


# 설정 검증 함수
def validate_settings() -> bool:
    """
    설정값들이 올바른지 검증하는 함수
    
    Returns:
        bool: 모든 설정이 올바르면 True, 아니면 False
    """
    try:
        # Redis URL 검증
        if not settings.redis_url:
            print("❌ Redis URL이 설정되지 않았습니다.")
            return False
            
        # Kafka 서버 검증
        if not settings.kafka_bootstrap_servers:
            print("❌ Kafka 브로커 서버가 설정되지 않았습니다.")
            return False
            
        # 데이터베이스 URL 검증
        if not settings.database_url:
            print("❌ 데이터베이스 URL이 설정되지 않았습니다.")
            return False
        
        if "tutorial_password" in settings.database_url:
            print("⚠️ 기본 데이터베이스 설정을 사용하고 있습니다. 운영 환경에서는 변경하세요.")
            
        # 시크릿 키 검증
        if "your-secret-key-here" in settings.secret_key or len(settings.secret_key) < 32:
            print("⚠️ 시크릿 키가 기본값이거나 너무 짧습니다. 보안을 위해 변경하세요.")
            
        print("✅ 모든 설정이 올바르게 구성되었습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 설정 검증 중 오류 발생: {e}")
        return False


if __name__ == "__main__":
    """
    이 파일을 직접 실행했을 때 설정 정보를 출력
    """
    print_settings()
    validate_settings()