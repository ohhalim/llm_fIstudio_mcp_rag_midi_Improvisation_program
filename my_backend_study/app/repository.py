from sqlalchemy.orm import Session
from app.model import Chat

def save_chat(db: Session, question: str, answer: str):
    """질문과 답변을 DB에 저장"""
    chat = Chat(question=question, answer=answer)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_all_chats(db: Session):
    """모든 채팅 가져오기 (최신순)"""
    return db.query(Chat).order_by(Chat.created_at.desc()).all()