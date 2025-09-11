from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declatative_base
from sqlalchemy.orm import sessionmaker
from .simple_config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metabata.create_all(bind=engine)
    