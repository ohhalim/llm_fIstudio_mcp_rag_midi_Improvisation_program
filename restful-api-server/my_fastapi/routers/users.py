from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os

# 상위 디렉터리의 모델을 import하기 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import User, UserCreate

router = APIRouter()

# 임시 데이터베이스 (실제로는 SQLAlchemy 사용)
fake_users_db = [
    {"id": 1, "name": "김철수", "email": "kim@example.com", "is_active": True},
    {"id": 2, "name": "이영희", "email": "lee@example.com", "is_active": True}
]

@router.get("/", response_model=List[User])
def get_users():
    """모든 사용자 조회"""
    return fake_users_db

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    """특정 사용자 조회"""
    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

@router.post("/", response_model=User)
def create_user(user: UserCreate):
    """새 사용자 생성"""
    new_user = {
        "id": len(fake_users_db) + 1,
        "name": user.name,
        "email": user.email,
        "is_active": True
    }
    fake_users_db.append(new_user)
    return new_user

@router.delete("/{user_id}")
def delete_user(user_id: int):
    """사용자 삭제"""
    for i, user in enumerate(fake_users_db):
        if user["id"] == user_id:
            del fake_users_db[i]
            return {"message": "사용자가 삭제되었습니다"}
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")