"""
API 패키지 초기화 파일
모든 API 라우터를 통합합니다.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .posts import router as posts_router
from .upload import router as upload_router

# 메인 API 라우터 생성
api_router = APIRouter(prefix="/api/v1")

# 각 기능별 라우터 등록
api_router.include_router(auth_router)      # /api/v1/auth/*
api_router.include_router(posts_router)     # /api/v1/posts/*
api_router.include_router(upload_router)    # /api/v1/files/*

__all__ = ["api_router"]