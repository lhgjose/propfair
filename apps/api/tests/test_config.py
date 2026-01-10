import os
import pytest
from propfair_api.config import Settings


def test_settings_loads_defaults():
    settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        redis_url="redis://localhost:6379",
        secret_key="test-secret",
    )
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000


def test_settings_uses_defaults():
    settings = Settings()
    assert settings.database_url == "sqlite:///:memory:"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.secret_key == "test-secret-key-not-for-production"
