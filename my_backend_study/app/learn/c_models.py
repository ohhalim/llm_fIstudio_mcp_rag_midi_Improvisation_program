from sqlalchemy import Column, Interger, String, DataTime
from sqlalchemy.sql import func
from .simple_database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Tnteger, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable =False)
    age = Column(Integer)
    created_at = Column(DateTime, dafault=func.now())