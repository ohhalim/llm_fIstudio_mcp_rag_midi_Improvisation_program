from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_tables
from .controller import router
from .config import settings

# FastAPI 앱 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 테이블 생성
    create_tables()
    yield
    # 앱 종료 시 처리 필요 시 여기에 작성

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

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