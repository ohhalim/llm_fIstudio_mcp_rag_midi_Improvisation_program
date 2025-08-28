from pydantic_settings import BaseSettiongs

class Settings(BaseSettings):
    redis_url: str ="redis://localhost:6379"
    kafka_bootstrap+servers: str ="localhost:9092"

    class Config:
        env_file = ".env"

settings = Settings()


