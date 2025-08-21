from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import httpx
import asyncio
from typing import Dict, Any
import sys
import os

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.config import get_settings
from shared.logging import setup_logging, get_logger, logging_middleware
from shared.auth import get_current_user

# 설정 초기화
settings = get_settings("gateway", 8000)
setup_logging("gateway")
logger = get_logger(__name__)

app = FastAPI(
    title="Music AI Gateway",
    description="API Gateway for Music AI Microservices",
    version="1.0.0"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적 도메인 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 신뢰할 수 있는 호스트 미들웨어
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # 프로덕션에서는 구체적 호스트 설정
)

# 로깅 미들웨어
app.middleware("http")(logging_middleware)

# HTTP 클라이언트
http_client = httpx.AsyncClient(timeout=30.0)

@app.on_event("startup")
async def startup_event():
    logger.info("API Gateway starting up")

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    logger.info("API Gateway shutting down")

# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway"}

# 서비스 라우팅
async def proxy_request(
    service_url: str,
    path: str,
    method: str,
    request: Request,
    user: Dict[str, Any] = None
) -> Dict[str, Any]:
    """다른 마이크로서비스로 요청 프록시"""
    
    url = f"{service_url}{path}"
    headers = dict(request.headers)
    
    # 인증 정보 전달
    if user:
        headers["X-User-ID"] = str(user.get("sub"))
        headers["X-User-Email"] = user.get("email", "")
    
    try:
        if method == "GET":
            response = await http_client.get(url, headers=headers, params=request.query_params)
        elif method == "POST":
            body = await request.body()
            response = await http_client.post(url, headers=headers, content=body)
        elif method == "PUT":
            body = await request.body()
            response = await http_client.put(url, headers=headers, content=body)
        elif method == "DELETE":
            response = await http_client.delete(url, headers=headers)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        }
    
    except httpx.RequestError as e:
        logger.error(f"Request to {url} failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error for {url}", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# User Service 라우팅
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_service_proxy(path: str, request: Request):
    response = await proxy_request(
        settings.service.user_service_url,
        f"/api/users/{path}",
        request.method,
        request
    )
    return response["content"]

# User Service 인증 라우팅 (인증 불필요)
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_service_proxy(path: str, request: Request):
    response = await proxy_request(
        settings.service.user_service_url,
        f"/api/auth/{path}",
        request.method,
        request
    )
    return response["content"]

# MIDI Service 라우팅 (인증 필요)
@app.api_route("/api/midi/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def midi_service_proxy(
    path: str, 
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user)
):
    response = await proxy_request(
        settings.service.midi_service_url,
        f"/api/midi/{path}",
        request.method,
        request,
        user
    )
    return response["content"]

# RAG Service 라우팅 (인증 필요)
@app.api_route("/api/rag/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def rag_service_proxy(
    path: str,
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user)
):
    response = await proxy_request(
        settings.service.rag_service_url,
        f"/api/rag/{path}",
        request.method,
        request,
        user
    )
    return response["content"]

# API 문서 집계
@app.get("/api/docs")
async def aggregate_docs():
    """모든 서비스의 API 문서 집계"""
    services = {
        "user": settings.service.user_service_url,
        "midi": settings.service.midi_service_url,
        "rag": settings.service.rag_service_url
    }
    
    docs = {}
    for service_name, service_url in services.items():
        try:
            response = await http_client.get(f"{service_url}/docs/openapi.json")
            if response.status_code == 200:
                docs[service_name] = response.json()
        except Exception as e:
            logger.warning(f"Could not fetch docs for {service_name}", error=str(e))
            docs[service_name] = {"error": "Service unavailable"}
    
    return docs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.service.service_host,
        port=settings.service.service_port,
        reload=settings.service.debug,
        log_config=None  # structlog 사용
    )