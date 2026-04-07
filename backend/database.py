# ──────────────────────────────────────────────
# database.py — SQLAlchemy engine & session setup
# Uses SQLite for development (swap URL for PostgreSQL in production)
# ──────────────────────────────────────────────

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite database URL — single file, zero setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./medicore.db"

# Create engine with SQLite-specific connect args
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory — each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
class Base(DeclarativeBase):
    pass
