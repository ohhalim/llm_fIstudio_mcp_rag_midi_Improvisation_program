from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .simple_database import get_db
from .simple_service import UserService
from .simple_schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_new_users(db, user)

@router.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return UserService.get_all_users(db, skip, limit)

@router.get("/users/{user_id}", resppnse_modle=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user_by_id(db, user_id)

@touter.put("/users/{user_id}", response_model= UserResponse)
def read_user(user_id: int db: Session = Depends