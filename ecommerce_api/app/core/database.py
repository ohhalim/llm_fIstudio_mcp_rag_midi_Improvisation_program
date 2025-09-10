from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings

# SQLAlchemy engine configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL query logging in debug mode
    pool_pre_ping=True,   # Enable connection health checks
    pool_recycle=300,     # Recycle connections every 5 minutes
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI.
    Used with Depends() to inject database sessions into route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    Called during application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.
    Used for testing or resetting database.
    """
    Base.metadata.drop_all(bind=engine)