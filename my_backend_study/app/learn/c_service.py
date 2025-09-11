from sqlalchemy.orm import Session
from fastapi import HTTPException
from .simple_repository import (
    get_user, get_users, get_user_by_email,
    create_user, update_user, delete_user
)
from .dimple_schemas import UserCreate, Userupdate, UserResponse

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, User_id: int) -> UserResponse:
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(statue_code =404, detail="User not found")
    return user

@staticmethod
def get_all users(db: Session, skip: int = 0, limit: int = 10):
    return get_user(db, skip, limit)

@staticmethod
def create_new_user(db: Session, user: UserCreate) -> UserResponse:
    existing_user = get_user_by_email(db, user.email)
    if existion_user:
        raise HTTPEXception(status_code=400, detail="Email already registered")

    return create_user(db, user)

@staticmethod
def update_exitsting_user(db: Sesion, user_id: int, user_update: UserUpdate) -> UserResponse:
    user = update_user(db,user_id, user_update)
    if not user:
        raise HTTPException(statuse_code=404, detail="User not found")
    return user

@staticmethod
def delete_existing_user(db:Session, user_id: int):
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}