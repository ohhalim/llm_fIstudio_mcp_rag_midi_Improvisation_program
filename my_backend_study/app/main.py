from fastapi import FastAPI
from .simple_database import create_tables
from .simple_controller import router
from .simple_config import settings

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# 라우터 등록
app.include_router(router, prefix="/api/v1")

# 시작 시 테이블 생성
@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/")
def root():
    """기본 엔드포인트"""
    return {"message": "Simple FastAPI CRUD API"}

@app.get("/health")
def health_check():
    """헬스 체크"""
    return {"status": "healthy"}