from fastapi import APIRouter
from models import User,UserCreate
from typing import List


router = APIRouter()

fake_items_db = []

@router.get("/", respoense_model=List[item])
def get_items():
    return fake_items_db
    
@router.get("/", response_model=List[Item])
def create_item(item: )
    new_user =(
        'id':len(fake_items_db) + 1 ,
        
    )

router.get("")