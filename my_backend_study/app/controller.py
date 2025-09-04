from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.service import ask_gemini, get_chat_history
from app.schemas import QuestionRequest, ChatResponse

router = APIRouter()

@router.post("/ask", response_model=ChatResponse)
def ask_question(question: QuestionRequest, db: Session = Depends(get_db)):
    """Gemini에게 질문하기"""
    chat = ask_gemini(db, question.question)
    return chat

@router.get("/history", response_model=List[ChatResponse])
def get_history(db: Session = Depends(get_db)):
    """채팅 히스토리 보기"""
    return get_chat_history(db)