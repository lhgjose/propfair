from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from propfair_api.config import settings

# Create engine with PostgreSQL-specific settings only for PostgreSQL
engine_kwargs = {"pool_pre_ping": True}
if settings.database_url.startswith("postgresql"):
    engine_kwargs.update({"pool_size": 10, "max_overflow": 20})

engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
