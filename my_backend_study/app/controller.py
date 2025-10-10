from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .service import UserService
from .schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """사용자 생성"""
    return UserService.create_new_user(db, user)

@router.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """사용자 목록 조회"""
    return UserService.get_all_users(db, skip, limit)

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """특정 사용자 조회"""
    return UserService.get_user_by_id(db, user_id)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """사용자 정보 업데이트"""
    return UserService.update_existing_user(db, user_id, user_update)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 삭제"""
    return UserService.delete_existing_user(db, user_id)