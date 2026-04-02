from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus Venture Backend"
    DATABASE_URL: str = "sqlite:///./nexus.db"
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    GEMINI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
