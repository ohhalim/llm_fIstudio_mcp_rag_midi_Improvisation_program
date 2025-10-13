from fastapi import FastAPI
from .database import create_tables
from .controller import router
from .config import settings

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

@app.on_event("startup")
def on_startup():
    create_tables()

# 라우터 등록
app.include_router(router, prefix="/api/v1")

# on_event("startup") 는 FastAPI 최신 버전에서 lifespan으로 대체됨

@app.get("/")
def root(): 
    
    """기본 엔드포인트"""
    return {"message": "Simple FastAPI CRUD API"}

@app.get("/health")
def health_check():
    """헬스 체크"""
    return {"status": "healthy"}