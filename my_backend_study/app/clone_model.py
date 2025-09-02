from sqlalchemy import Column, Integer, String, DateTime, Boolean
from dqlalchemy.sql import func

class User(base):
    __tablename__ = "users"

    id =Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at =Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.emails})"