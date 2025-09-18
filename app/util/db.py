from typing import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session


SQLALCHEMY_DATABASE_URL = "sqlite:///./database/app.db"

# Ensure directory exists for SQLite file
_db_dir = os.path.dirname(SQLALCHEMY_DATABASE_URL.replace("sqlite:///", ""))
if _db_dir and not os.path.exists(_db_dir):
    os.makedirs(_db_dir, exist_ok=True)

# For SQLite, check_same_thread must be False when using it with FastAPI in threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


