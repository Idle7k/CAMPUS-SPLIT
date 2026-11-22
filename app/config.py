from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "campus-split-local-development-secret-key-replace-in-prod-xyz789"
    DATABASE_URL: str = "sqlite:///./campus_split.db"
    
    # Session
    SESSION_COOKIE_NAME: str = "campus_split_session"
    SESSION_MAX_AGE: int = 86400  # 24 hours in seconds
    
    # Demo seed defaults
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    STUDENT_DEFAULT_PASSWORD: str = "student123"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
