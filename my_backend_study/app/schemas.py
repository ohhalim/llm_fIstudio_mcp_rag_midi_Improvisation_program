from pydantic import BaseModel
from datetime import datetime

# 질문 받을 때
class QuestionRequest(BaseModel):
    question: str

# 답변 보낼 때  
class ChatResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
    
    class Config:
        from_attributes = True