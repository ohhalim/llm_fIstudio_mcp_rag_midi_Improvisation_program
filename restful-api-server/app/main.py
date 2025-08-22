"""
FastAPI 메인 애플리케이션
모든 기능을 통합하고 서버를 시작하는 진입점입니다.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
import uvicorn

from app.core.config import settings
from app.db.database import engine
from app.models import Base  # 모든 모델을 import하여 테이블 생성
from app.api import api_router

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="RESTful API 서버",
    description="""
    **백엔드 취업 준비를 위한 실무 중심 RESTful API 서버**
    
    ## 주요 기능
    
    ### 🔐 인증 시스템
    - JWT 기반 회원가입/로그인
    - 보안 토큰 인증
    - 사용자 권한 관리
    
    ### 📝 게시판 기능
    - CRUD 게시글 관리
    - 페이징 및 검색
    - 작성자별 게시글 조회
    
    ### 📎 파일 관리
    - 단일/다중 파일 업로드
    - 파일 다운로드
    - 게시글과 파일 연동
    
    ### 🚀 기술 스택
    - **Backend**: FastAPI, Python
    - **Database**: PostgreSQL, SQLAlchemy
    - **Authentication**: JWT, BCrypt
    - **File Handling**: Async File Operations
    """,
    version="1.0.0",
    contact={
        "name": "개발자",
        "email": "developer@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS 미들웨어 설정 (프론트엔드와 연동을 위해 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # 허용할 도메인 목록
    allow_credentials=True,                  # 쿠키 및 인증 정보 허용
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 허용할 HTTP 메서드
    allow_headers=["*"],                     # 모든 헤더 허용
)

# 신뢰할 수 있는 호스트 미들웨어 (보안 강화)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# API 라우터 등록
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트
    데이터베이스 테이블을 자동으로 생성합니다.
    """
    try:
        # 모든 테이블 생성 (이미 존재하면 무시)
        Base.metadata.create_all(bind=engine)
        print("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다.")
        
        # 업로드 디렉토리 생성
        import os
        os.makedirs(settings.upload_dir, exist_ok=True)
        print(f"✅ 파일 업로드 디렉토리가 준비되었습니다: {settings.upload_dir}")
        
    except SQLAlchemyError as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
    except Exception as e:
        print(f"❌ 시작 시 오류 발생: {e}")

@app.get("/", include_in_schema=False)
async def root():
    """
    루트 경로 - API 문서로 리다이렉트
    """
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """
    서버 상태 확인 엔드포인트
    로드밸런서나 모니터링 도구에서 사용
    """
    return {
        "status": "healthy",
        "message": "RESTful API 서버가 정상적으로 동작 중입니다.",
        "version": "1.0.0"
    }

# 전역 예외 처리기
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """
    서버 내부 오류 처리
    """
    return HTTPException(
        status_code=500,
        detail="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    )

if __name__ == "__main__":
    # 직접 실행 시 개발 서버 시작
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,  # 개발 모드에서는 파일 변경 시 자동 재시작
        log_level="info"
    )