import os
from pydantic_settings import BaseSettings

class Settings(BassSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./simple_app.db")
    APP_NAME: str = "Simple FastAPI App"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()
