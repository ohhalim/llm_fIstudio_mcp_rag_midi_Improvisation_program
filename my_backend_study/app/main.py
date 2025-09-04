from fastapi import FastAPI
from app.database import create_tables
from app.controller import router

app = FastAPI(title="Gemini Chat API")

app.include_router(router)

@app.on_event("startup")
def startup():
    create_tables()

@app.get("/")
def root():
    return {"message": "Gemini Chat API 시작!"}