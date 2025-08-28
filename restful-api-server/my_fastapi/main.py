from fastapi import FastAPI
from routers import users

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="My FastAPI App",
    description="Django 경험자를 위한 FastAPI 학습용 API",
    version="1.0.0"
)

# 라우터 포함
app.include_router(users.router, prefix="/users", tags=["users"])

# 기본 루트 엔드포인트
@app.get("/")
def read_root():
    return {
        "message": "Hello FastAPI!",
        "status": "running",
        "version": "1.0.0",
        "available_endpoints": {
            "users": "/users",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# 간단한 헬스체크 엔드포인트
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 쿼리 매개변수 예제
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {
        "skip": skip,
        "limit": limit,
        "message": "이것은 쿼리 매개변수 예제입니다"
    }
