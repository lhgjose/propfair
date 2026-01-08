import pytest
from propfair_api.database import get_db_session


def test_get_db_session_returns_generator():
    gen = get_db_session()
    assert hasattr(gen, "__next__")
