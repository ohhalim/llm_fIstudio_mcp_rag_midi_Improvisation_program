"""
main.py - FastAPI 애플리케이션 메인 파일

이 파일에서 배울 수 있는 개념들:
1. FastAPI 애플리케이션 구성
2. 라이프사이클 이벤트 처리 (startup/shutdown)
3. 미들웨어 설정
4. CORS 설정
5. 예외 처리 (Exception Handling)
6. 헬스체크 엔드포인트
7. API 문서화 설정
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
import uvicorn
import logging
import time
from datetime import datetime
from typing import Dict, Any
import sys
import os

# 프로젝트 모듈 import
from config import settings, print_settings, validate_settings
from routers import users, events
from services.redis_service import redis_service
from services.kafka_service import kafka_service
from models import HealthCheck


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),     # 로그 파일
        logging.StreamHandler(sys.stdout)   # 콘솔 출력
    ]
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    FastAPI 애플리케이션 팩토리 함수
    
    애플리케이션을 생성하고 모든 설정을 구성합니다.
    테스트나 다른 환경에서 다른 설정으로 애플리케이션을 만들 때 유용합니다.
    
    Returns:
        FastAPI: 구성된 FastAPI 애플리케이션
    """
    
    # FastAPI 애플리케이션 생성
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        ## FastAPI + Kafka + Redis 튜토리얼 API

        이 API는 다음 기능을 제공합니다:

        ### 🧑‍💼 사용자 관리
        - 사용자 생성, 조회, 수정, 삭제
        - 사용자 인증 및 로그인
        - 사용자 통계 조회

        ### 📨 이벤트 처리
        - 실시간 이벤트 발행
        - Kafka 토픽 관리
        - 이벤트 통계 모니터링

        ### 🔧 기술 스택
        - **FastAPI**: 현대적인 Python 웹 프레임워크
        - **Redis**: 캐시 및 세션 저장소
        - **Apache Kafka**: 메시지 큐 및 이벤트 스트리밍
        - **Pydantic**: 데이터 검증 및 직렬화
        - **Docker**: 컨테이너화된 개발 환경

        ### 📚 학습 목적
        이 프로젝트는 마이크로서비스 아키텍처의 핵심 개념들을 학습하기 위해 설계되었습니다.
        """,
        docs_url="/docs" if settings.debug else None,  # 프로덕션에서는 문서 비활성화
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        debug=settings.debug
    )
    
    # 미들웨어 설정
    setup_middleware(app)
    
    # 라우터 등록
    setup_routers(app)
    
    # 예외 처리기 등록
    setup_exception_handlers(app)
    
    # 라이프사이클 이벤트 등록
    setup_lifecycle_events(app)
    
    # 커스텀 OpenAPI 스키마 (선택사항)
    setup_custom_openapi(app)
    
    return app


def setup_middleware(app: FastAPI):
    """
    미들웨어 설정
    
    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스
    """
    
    # CORS 미들웨어 (Cross-Origin Resource Sharing)
    # 웹 브라우저에서 다른 도메인의 API를 호출할 수 있게 해줍니다
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [
            "http://localhost:3000",  # React 개발 서버
            "http://localhost:8080",  # Vue 개발 서버
            "https://yourdomain.com"  # 프로덕션 도메인
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 신뢰할 수 있는 호스트 미들웨어 (보안)
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
        )
    
    # 커스텀 미들웨어: 요청 로깅 및 처리 시간 측정
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        HTTP 요청 로깅 미들웨어
        
        모든 HTTP 요청의 처리 시간을 측정하고 로그를 남깁니다.
        """
        start_time = time.time()
        
        # 요청 정보 로깅
        logger.info(f"🔄 {request.method} {request.url.path} - 처리 시작")
        
        # 실제 엔드포인트 처리
        response = await call_next(request)
        
        # 처리 시간 계산
        process_time = time.time() - start_time
        
        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)
        
        # 완료 로깅
        logger.info(
            f"✅ {request.method} {request.url.path} - "
            f"상태: {response.status_code}, 처리시간: {process_time:.4f}초"
        )
        
        return response


def setup_routers(app: FastAPI):
    """
    API 라우터 등록
    
    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스
    """
    
    # API v1 라우터들 등록
    app.include_router(
        users.router,
        prefix="/api/v1",
        tags=["users"]
    )
    
    app.include_router(
        events.router,
        prefix="/api/v1",
        tags=["events"]
    )
    
    logger.info("✅ API 라우터 등록 완료")


def setup_exception_handlers(app: FastAPI):
    """
    전역 예외 처리기 설정
    
    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        HTTP 예외 처리기
        
        일관된 에러 응답 형식을 제공합니다.
        """
        logger.error(f"❌ HTTP 에러: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "timestamp": datetime.now().isoformat(),
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        일반 예외 처리기
        
        예상치 못한 서버 에러를 안전하게 처리합니다.
        """
        logger.error(f"❌ 예상치 못한 에러: {type(exc).__name__}: {str(exc)}")
        
        # 디버그 모드에서만 상세 에러 정보 노출
        error_detail = str(exc) if settings.debug else "내부 서버 오류가 발생했습니다"
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": 500,
                    "message": error_detail,
                    "timestamp": datetime.now().isoformat(),
                    "path": request.url.path
                }
            }
        )


def setup_lifecycle_events(app: FastAPI):
    """
    애플리케이션 라이프사이클 이벤트 설정
    
    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스
    """
    
    @app.on_event("startup")
    async def startup_event():
        """
        애플리케이션 시작 시 실행되는 이벤트
        
        필요한 초기화 작업을 수행합니다:
        - 설정 검증
        - 외부 서비스 연결 확인
        - 필수 토픽 생성
        """
        logger.info("🚀 FastAPI 애플리케이션 시작")
        
        try:
            # 1. 설정 정보 출력
            print_settings()
            
            # 2. 설정 검증
            if not validate_settings():
                logger.error("❌ 설정 검증 실패 - 애플리케이션을 종료합니다")
                sys.exit(1)
            
            # 3. Redis 연결 확인
            redis_health = await redis_service.health_check()
            if redis_health["status"] != "healthy":
                logger.warning(f"⚠️ Redis 연결 문제: {redis_health['message']}")
            else:
                logger.info("✅ Redis 연결 확인")
            
            # 4. Kafka 연결 확인
            kafka_health = await kafka_service.health_check()
            if kafka_health["status"] != "healthy":
                logger.warning(f"⚠️ Kafka 연결 문제: {kafka_health['message']}")
            else:
                logger.info("✅ Kafka 연결 확인")
            
            # 5. 필수 토픽 생성
            required_topics = [
                ("user_events", 3, 1),      # (토픽명, 파티션수, 복제본수)
                ("system_events", 2, 1),
                ("notifications", 1, 1)
            ]
            
            for topic_name, partitions, replication in required_topics:
                success = await kafka_service.create_topic(
                    topic_name=topic_name,
                    num_partitions=partitions,
                    replication_factor=replication
                )
                if success:
                    logger.info(f"📝 토픽 확인/생성: {topic_name}")
            
            logger.info("✅ 애플리케이션 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 시작 이벤트 중 오류: {e}")
            # 치명적 오류의 경우 애플리케이션 종료
            sys.exit(1)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """
        애플리케이션 종료 시 실행되는 이벤트
        
        정리 작업을 수행합니다:
        - 연결 종료
        - 리소스 정리
        - 최종 로그
        """
        logger.info("🛑 FastAPI 애플리케이션 종료 시작")
        
        try:
            # 1. Kafka 연결 종료
            if kafka_service:
                kafka_service.close()
                logger.info("✅ Kafka 연결 종료")
            
            # 2. Redis 연결 종료
            if redis_service:
                redis_service.close_connection()
                logger.info("✅ Redis 연결 종료")
            
            logger.info("✅ 애플리케이션 정상 종료 완료")
            
        except Exception as e:
            logger.error(f"❌ 종료 이벤트 중 오류: {e}")


def setup_custom_openapi(app: FastAPI):
    """
    커스텀 OpenAPI 스키마 설정
    
    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스
    """
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=settings.app_name,
            version=settings.app_version,
            description=app.description,
            routes=app.routes,
        )
        
        # 커스텀 스키마 정보 추가
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        
        # 보안 스키마 추가 (JWT 등)
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi


# 애플리케이션 인스턴스 생성
app = create_application()


# 기본 엔드포인트들

@app.get("/", summary="루트 엔드포인트", tags=["기본"])
async def root() -> Dict[str, Any]:
    """
    루트 엔드포인트
    
    애플리케이션의 기본 정보를 반환합니다.
    """
    return {
        "message": f"{settings.app_name}에 오신 것을 환영합니다!",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "timestamp": datetime.now().isoformat(),
        "status": "running"
    }


@app.get("/health", response_model=HealthCheck, summary="전체 헬스체크", tags=["모니터링"])
async def health_check() -> HealthCheck:
    """
    전체 시스템 헬스체크
    
    애플리케이션과 모든 의존 서비스의 상태를 확인합니다.
    
    Returns:
        HealthCheck: 시스템 전체 상태 정보
    """
    try:
        # 각 서비스별 헬스체크
        redis_health = await redis_service.health_check()
        kafka_health = await kafka_service.health_check()
        
        # 전체 상태 결정
        services = {
            "redis": redis_health["status"],
            "kafka": kafka_health["status"],
            "application": "healthy"
        }
        
        # 하나라도 unhealthy면 전체 상태를 degraded로 설정
        overall_status = "healthy"
        if any(status != "healthy" for status in services.values()):
            overall_status = "degraded"
        
        return HealthCheck(
            status=overall_status,
            services=services,
            version=settings.app_version
        )
        
    except Exception as e:
        logger.error(f"❌ 헬스체크 중 오류: {e}")
        
        return HealthCheck(
            status="unhealthy",
            services={"error": str(e)},
            version=settings.app_version
        )


@app.get("/metrics", summary="애플리케이션 메트릭", tags=["모니터링"])
async def get_metrics() -> Dict[str, Any]:
    """
    애플리케이션 메트릭 조회
    
    모니터링 시스템에서 사용할 수 있는 메트릭 정보를 반환합니다.
    실제 환경에서는 Prometheus 등의 메트릭 시스템과 연동합니다.
    
    Returns:
        Dict[str, Any]: 메트릭 정보
    """
    try:
        # Redis 통계
        redis_stats = await redis_service.get_cache_stats()
        
        # 기본 애플리케이션 메트릭
        metrics = {
            "application": {
                "name": settings.app_name,
                "version": settings.app_version,
                "uptime_seconds": time.time() - getattr(app, '_start_time', time.time()),
                "debug_mode": settings.debug
            },
            "redis": redis_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"❌ 메트릭 조회 중 오류: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# 개발용 엔드포인트 (디버그 모드에서만)
if settings.debug:
    @app.get("/debug/info", summary="디버그 정보", tags=["디버그"])
    async def debug_info():
        """디버그용 시스템 정보 (개발 환경에서만 사용)"""
        import psutil
        import platform
        
        return {
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            },
            "application": {
                "name": settings.app_name,
                "version": settings.app_version,
                "debug": settings.debug,
                "routes_count": len(app.routes)
            },
            "environment": dict(os.environ) if settings.debug else "Hidden in production"
        }


# 애플리케이션 시작 시간 기록
app._start_time = time.time()


if __name__ == "__main__":
    """
    개발 서버 실행
    
    이 블록은 스크립트를 직접 실행했을 때만 동작합니다.
    실제 배포에서는 gunicorn, uvicorn 등을 사용합니다.
    
    사용법:
        python main.py
    """
    logger.info("🔧 개발 서버 시작")
    
    # 개발 서버 설정
    uvicorn.run(
        "main:app",  # 애플리케이션 모듈:인스턴스
        host="0.0.0.0",  # 모든 인터페이스에서 접근 허용
        port=8000,       # 포트 번호
        reload=settings.debug,  # 코드 변경 시 자동 재시작 (개발 모드만)
        log_level="info",
        access_log=True,
        reload_dirs=["./"] if settings.debug else None,  # 감시할 디렉토리
        reload_excludes=["*.log", "__pycache__", "*.pyc"] if settings.debug else None
    )