from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="sqlite:///:memory:")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = Field(default="test-secret-key-not-for-production")
    debug: bool = False

    # Auth
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
