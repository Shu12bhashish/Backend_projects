from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    WEBHOOK_SECRET: str
    LOG_LEVEL: str = "INFO"

settings = Settings()
