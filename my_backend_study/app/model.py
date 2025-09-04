from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True)
    question = Column(Text)  # 질문
    answer = Column(Text)    # 답변
    created_at = Column(DateTime, default=func.now())