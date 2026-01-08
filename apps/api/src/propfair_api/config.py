from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str

    # Redis
    redis_url: str

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str
    debug: bool = False

    # Auth
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
