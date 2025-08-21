from pydantic_settings import BaseSettings
from typing import Optional


class DatabaseSettings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/musicdb"
    echo: bool = False
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_prefix = "REDIS_"


class AuthSettings(BaseSettings):
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_prefix = "AUTH_"


class ServiceSettings(BaseSettings):
    service_name: str
    service_host: str = "0.0.0.0"
    service_port: int
    debug: bool = False
    
    # 다른 서비스 엔드포인트
    gateway_url: str = "http://localhost:8000"
    user_service_url: str = "http://localhost:8001"
    midi_service_url: str = "http://localhost:8002"
    rag_service_url: str = "http://localhost:8003"
    
    class Config:
        env_prefix = "SERVICE_"


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    auth: AuthSettings = AuthSettings()
    service: ServiceSettings
    
    class Config:
        env_file = ".env"


def get_settings(service_name: str, service_port: int) -> Settings:
    return Settings(
        service=ServiceSettings(
            service_name=service_name,
            service_port=service_port
        )
    )