import structlog
import logging
import sys
from typing import Optional

def setup_logging(service_name: str, level: str = "INFO") -> None:
    """구조화된 로깅 설정"""
    
    # 표준 라이브러리 로깅 설정
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )
    
    # structlog 설정
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer()  # 개발용, 프로덕션에서는 JSONRenderer 사용
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 서비스 이름을 기본 컨텍스트에 추가
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """구조화된 로거 인스턴스 반환"""
    return structlog.get_logger(name)


# HTTP 요청 로깅을 위한 미들웨어
from fastapi import Request, Response
from fastapi.routing import Match
import time

async def logging_middleware(request: Request, call_next):
    """HTTP 요청/응답 로깅 미들웨어"""
    logger = get_logger("http")
    
    start_time = time.time()
    
    # 요청 로깅
    logger.info(
        "HTTP request started",
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        client_ip=request.client.host if request.client else None
    )
    
    # 응답 처리
    response = await call_next(request)
    
    # 응답 로깅
    process_time = time.time() - start_time
    logger.info(
        "HTTP request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4),
        response_headers=dict(response.headers)
    )
    
    return response