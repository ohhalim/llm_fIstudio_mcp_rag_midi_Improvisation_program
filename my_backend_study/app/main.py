from fastapi import FastAPI
from .database import create_tables
from .controller import router
from .config import settings

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# 라우터 등록
app.include_router(router)

# 애플리케이션 시작 시 테이블 생성
@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/")
def root():
    """기본 엔드포인트"""
    return {"message": "FastAPI CRUD API with PostgreSQL"}

@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

