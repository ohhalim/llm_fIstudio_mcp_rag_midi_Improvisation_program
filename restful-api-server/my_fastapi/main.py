# from fastapi import FastAPI
# from routers import users, items

# app = Fast  (title ="My API", version = '1.0.0')

# app.include_router(users.router, perfix"/users", tags = ["users"])
# app.include_router(items.router, perfix"/items", tags =["items"])


# @app.get("/")
# def read_root():
#     return {"message": 'hello world'}


## 오늘 저거 다치쟈 fastapi 최소구현 코드  -> 0 다 했다!!

from fastapi import FastAPI

app = FastAPI()

@app,get("/")
def read_root():
    return {"Hello": "World"}

# Model
class User(models.Model):
    name = models.CharField(max_length=100)
    email = modles.EmailField()

from pydantic import BaseModel

class User(BaseModel):
    name:str
    email: str

@app.get("/users/{user_id}")
def read_user(user_id: int, q: str = None):
    return {"user_id": user_id, "q":q}


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Uesr(Base):
    --tablename-- = "users"
    id = Clomn(Integer, primary_key=True, index=True)
    name =Column(String, index=True)

from fastapi import Depends

def get_db():
    db = SessinLocal()
    try:
        yield db
    finally: 
        db.close()

@app.get("/users/")
def read_users(db:Sesion = Depends(get_db)):
    return db.query(User).all()
