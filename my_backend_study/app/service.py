import google.generativeai as genai
from sqlalchemy.orm import Session
from app.repository import save_chat, get_all_chats
from app.config import settings

# Gemini 설정
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

def ask_gemini(db: Session, question: str):
    """Gemini에게 질문하고 DB에 저장"""
    # Gemini에게 질문
    response = model.generate_content(question)
    answer = response.text
    
    # DB에 저장
    chat = save_chat(db, question, answer)
    return chat

def get_chat_history(db: Session):
    """채팅 히스토리 가져오기"""
    return get_all_chats(db)