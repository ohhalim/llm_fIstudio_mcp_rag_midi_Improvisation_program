"""
routers/users.py - 사용자 관련 API 라우터

이 파일에서 배울 수 있는 개념들:
1. FastAPI 라우터 패턴
2. 의존성 주입 (Dependency Injection)
3. HTTP 상태 코드와 예외 처리
4. 요청/응답 모델 활용
5. API 문서화 (OpenAPI)
6. 입력 데이터 검증
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from models import (
    User, UserCreate, UserUpdate, UserStatus, 
    APIResponse, PaginatedResponse, UserStats
)
from services.user_service import user_service


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(
    prefix="/users",  # 모든 경로에 /users 접두사 추가
    tags=["users"],   # OpenAPI 문서에서 그룹화
    responses={
        404: {"description": "사용자를 찾을 수 없습니다"},
        422: {"description": "입력 데이터 검증 실패"}
    }
)


# 의존성 함수들
async def get_user_service():
    """
    사용자 서비스 의존성
    
    의존성 주입 패턴을 사용하여 서비스를 주입받습니다.
    테스트할 때 모킹된 서비스로 교체할 수 있어 유용합니다.
    """
    return user_service


def validate_user_id(user_id: int) -> int:
    """
    사용자 ID 검증 의존성
    
    Args:
        user_id (int): 검증할 사용자 ID
        
    Returns:
        int: 검증된 사용자 ID
        
    Raises:
        HTTPException: ID가 유효하지 않을 때
    """
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 ID는 양수여야 합니다"
        )
    return user_id


# API 엔드포인트들

@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새 사용자 생성",
    description="새로운 사용자를 생성합니다. 이메일은 중복될 수 없습니다.",
    response_description="생성된 사용자 정보"
)
async def create_user(
    user_data: UserCreate,
    service: Any = Depends(get_user_service)
) -> APIResponse:
    """
    새 사용자 생성 엔드포인트
    
    Args:
        user_data (UserCreate): 사용자 생성 정보
        service: 의존성으로 주입받은 사용자 서비스
        
    Returns:
        APIResponse: 표준 API 응답
        
    Raises:
        HTTPException: 이메일 중복 또는 생성 실패 시
    """
    try:
        logger.info(f"🔄 사용자 생성 요청: {user_data.email}")
        
        # 사용자 생성
        new_user = await service.create_user(user_data)
        
        if not new_user:
            # 이메일 중복 등의 이유로 생성 실패
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="사용자 생성에 실패했습니다. 이메일이 이미 존재할 수 있습니다."
            )
        
        logger.info(f"✅ 사용자 생성 성공: {new_user.id}")\n        \n        return APIResponse(\n            success=True,\n            message=\"사용자가 성공적으로 생성되었습니다\",\n            data=new_user.dict()\n        )\n        \n    except HTTPException:\n        # HTTP 예외는 그대로 재발생\n        raise\n    except Exception as e:\n        logger.error(f\"❌ 사용자 생성 중 예상치 못한 오류: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"서버 오류가 발생했습니다\"\n        )\n\n\n@router.get(\n    \"/{user_id}\",\n    response_model=APIResponse,\n    summary=\"사용자 정보 조회\",\n    description=\"사용자 ID로 특정 사용자의 정보를 조회합니다.\",\n    responses={\n        200: {\"description\": \"사용자 정보 조회 성공\"},\n        404: {\"description\": \"사용자를 찾을 수 없음\"}\n    }\n)\nasync def get_user(\n    user_id: int = Depends(validate_user_id),\n    service: Any = Depends(get_user_service)\n) -> APIResponse:\n    \"\"\"\n    사용자 정보 조회 엔드포인트\n    \n    Args:\n        user_id (int): 조회할 사용자 ID (의존성으로 검증됨)\n        service: 의존성으로 주입받은 사용자 서비스\n        \n    Returns:\n        APIResponse: 사용자 정보가 포함된 응답\n        \n    Raises:\n        HTTPException: 사용자를 찾을 수 없을 때\n    \"\"\"\n    try:\n        logger.info(f\"🔍 사용자 조회 요청: {user_id}\")\n        \n        user = await service.get_user(user_id)\n        \n        if not user:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=f\"사용자 ID {user_id}를 찾을 수 없습니다\"\n            )\n        \n        logger.info(f\"✅ 사용자 조회 성공: {user_id}\")\n        \n        return APIResponse(\n            success=True,\n            message=\"사용자 정보 조회 성공\",\n            data=user.dict()\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"❌ 사용자 조회 중 오류 ({user_id}): {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"사용자 조회 중 오류가 발생했습니다\"\n        )\n\n\n@router.put(\n    \"/{user_id}\",\n    response_model=APIResponse,\n    summary=\"사용자 정보 수정\",\n    description=\"사용자 ID로 특정 사용자의 정보를 수정합니다.\"\n)\nasync def update_user(\n    user_update: UserUpdate,\n    user_id: int = Depends(validate_user_id),\n    service: Any = Depends(get_user_service)\n) -> APIResponse:\n    \"\"\"\n    사용자 정보 수정 엔드포인트\n    \n    Args:\n        user_update (UserUpdate): 수정할 사용자 정보\n        user_id (int): 수정할 사용자 ID\n        service: 의존성으로 주입받은 사용자 서비스\n        \n    Returns:\n        APIResponse: 수정된 사용자 정보가 포함된 응답\n    \"\"\"\n    try:\n        logger.info(f\"🔄 사용자 수정 요청: {user_id}\")\n        \n        updated_user = await service.update_user(user_id, user_update)\n        \n        if not updated_user:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=f\"수정할 사용자 ID {user_id}를 찾을 수 없습니다\"\n            )\n        \n        logger.info(f\"✅ 사용자 수정 성공: {user_id}\")\n        \n        return APIResponse(\n            success=True,\n            message=\"사용자 정보가 성공적으로 수정되었습니다\",\n            data=updated_user.dict()\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"❌ 사용자 수정 중 오류 ({user_id}): {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"사용자 수정 중 오류가 발생했습니다\"\n        )\n\n\n@router.delete(\n    \"/{user_id}\",\n    response_model=APIResponse,\n    summary=\"사용자 삭제\",\n    description=\"사용자 ID로 특정 사용자를 삭제합니다 (소프트 삭제).\"\n)\nasync def delete_user(\n    user_id: int = Depends(validate_user_id),\n    service: Any = Depends(get_user_service)\n) -> APIResponse:\n    \"\"\"\n    사용자 삭제 엔드포인트 (소프트 삭제)\n    \n    실제로는 데이터를 삭제하지 않고 상태만 변경합니다.\n    \n    Args:\n        user_id (int): 삭제할 사용자 ID\n        service: 의존성으로 주입받은 사용자 서비스\n        \n    Returns:\n        APIResponse: 삭제 결과 응답\n    \"\"\"\n    try:\n        logger.info(f\"🗑️ 사용자 삭제 요청: {user_id}\")\n        \n        success = await service.delete_user(user_id)\n        \n        if not success:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=f\"삭제할 사용자 ID {user_id}를 찾을 수 없습니다\"\n            )\n        \n        logger.info(f\"✅ 사용자 삭제 성공: {user_id}\")\n        \n        return APIResponse(\n            success=True,\n            message=\"사용자가 성공적으로 삭제되었습니다\",\n            data={\"deleted_user_id\": user_id}\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"❌ 사용자 삭제 중 오류 ({user_id}): {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"사용자 삭제 중 오류가 발생했습니다\"\n        )\n\n\n@router.get(\n    \"/\",\n    response_model=PaginatedResponse,\n    summary=\"사용자 목록 조회\",\n    description=\"페이지네이션과 필터링을 지원하는 사용자 목록을 조회합니다.\"\n)\nasync def list_users(\n    skip: int = Query(0, ge=0, description=\"건너뛸 개수\"),\n    limit: int = Query(10, ge=1, le=100, description=\"최대 조회 개수 (1-100)\"),\n    status: Optional[UserStatus] = Query(None, description=\"필터링할 사용자 상태\"),\n    service: Any = Depends(get_user_service)\n) -> PaginatedResponse:\n    \"\"\"\n    사용자 목록 조회 엔드포인트\n    \n    페이지네이션과 상태 필터링을 지원합니다.\n    \n    Args:\n        skip (int): 건너뛸 개수 (페이지네이션용)\n        limit (int): 최대 조회 개수 (1-100 제한)\n        status (Optional[UserStatus]): 필터링할 사용자 상태\n        service: 의존성으로 주입받은 사용자 서비스\n        \n    Returns:\n        PaginatedResponse: 페이지네이션된 사용자 목록\n    \"\"\"\n    try:\n        logger.info(f\"📋 사용자 목록 조회: skip={skip}, limit={limit}, status={status}\")\n        \n        users = await service.list_users(skip=skip, limit=limit, status=status)\n        \n        # 전체 개수는 실제 환경에서는 별도로 조회해야 함\n        # 여기서는 단순화를 위해 현재 조회된 개수로 설정\n        total = len(users) + skip  # 근사치\n        \n        # 페이지 계산\n        page = (skip // limit) + 1 if limit > 0 else 1\n        total_pages = (total + limit - 1) // limit if limit > 0 else 1\n        \n        logger.info(f\"✅ 사용자 목록 조회 성공: {len(users)}명\")\n        \n        return PaginatedResponse(\n            items=[user.dict() for user in users],\n            total=total,\n            page=page,\n            size=limit,\n            pages=total_pages\n        )\n        \n    except Exception as e:\n        logger.error(f\"❌ 사용자 목록 조회 중 오류: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"사용자 목록 조회 중 오류가 발생했습니다\"\n        )\n\n\n@router.post(\n    \"/auth/login\",\n    response_model=APIResponse,\n    summary=\"사용자 로그인\",\n    description=\"이메일과 비밀번호로 사용자 인증을 수행합니다.\",\n    responses={\n        200: {\"description\": \"로그인 성공\"},\n        401: {\"description\": \"인증 실패\"}\n    }\n)\nasync def login_user(\n    email: str = Query(..., description=\"이메일 주소\"),\n    password: str = Query(..., description=\"비밀번호\"),\n    service: Any = Depends(get_user_service)\n) -> APIResponse:\n    \"\"\"\n    사용자 로그인 엔드포인트\n    \n    실제 환경에서는 JWT 토큰을 발급하고 보안을 강화해야 합니다.\n    \n    Args:\n        email (str): 이메일 주소\n        password (str): 비밀번호\n        service: 의존성으로 주입받은 사용자 서비스\n        \n    Returns:\n        APIResponse: 로그인 성공 시 사용자 정보 포함\n        \n    Raises:\n        HTTPException: 인증 실패 시\n    \"\"\"\n    try:\n        logger.info(f\"🔐 로그인 요청: {email}\")\n        \n        user = await service.authenticate_user(email, password)\n        \n        if not user:\n            # 보안을 위해 구체적인 실패 이유를 노출하지 않음\n            raise HTTPException(\n                status_code=status.HTTP_401_UNAUTHORIZED,\n                detail=\"이메일 또는 비밀번호가 올바르지 않습니다\"\n            )\n        \n        logger.info(f\"✅ 로그인 성공: {email}\")\n        \n        # 실제 환경에서는 JWT 토큰을 생성하여 반환\n        return APIResponse(\n            success=True,\n            message=\"로그인에 성공했습니다\",\n            data={\n                \"user\": user.dict(),\n                \"token\": f\"mock_jwt_token_for_user_{user.id}\"  # 실제로는 JWT 생성\n            }\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"❌ 로그인 중 오류 ({email}): {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"로그인 처리 중 오류가 발생했습니다\"\n        )\n\n\n@router.get(\n    \"/stats/overview\",\n    response_model=APIResponse,\n    summary=\"사용자 통계 조회\",\n    description=\"전체 사용자 통계 정보를 조회합니다.\"\n)\nasync def get_user_statistics(\n    service: Any = Depends(get_user_service)\n) -> APIResponse:\n    \"\"\"\n    사용자 통계 조회 엔드포인트\n    \n    관리자나 대시보드에서 사용할 수 있는 통계 정보를 제공합니다.\n    \n    Args:\n        service: 의존성으로 주입받은 사용자 서비스\n        \n    Returns:\n        APIResponse: 사용자 통계 정보가 포함된 응답\n    \"\"\"\n    try:\n        logger.info(\"📊 사용자 통계 조회 요청\")\n        \n        stats = await service.get_user_stats()\n        \n        logger.info(\"✅ 사용자 통계 조회 성공\")\n        \n        return APIResponse(\n            success=True,\n            message=\"사용자 통계 조회 성공\",\n            data=stats\n        )\n        \n    except Exception as e:\n        logger.error(f\"❌ 사용자 통계 조회 중 오류: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"사용자 통계 조회 중 오류가 발생했습니다\"\n        )\n\n\n@router.get(\n    \"/health\",\n    summary=\"사용자 서비스 헬스체크\",\n    description=\"사용자 서비스의 상태를 확인합니다.\"\n)\nasync def health_check(\n    service: Any = Depends(get_user_service)\n) -> Dict[str, str]:\n    \"\"\"\n    사용자 서비스 헬스체크 엔드포인트\n    \n    서비스의 의존성들(Redis, Kafka 등)의 상태도 간접적으로 확인할 수 있습니다.\n    \n    Args:\n        service: 의존성으로 주입받은 사용자 서비스\n        \n    Returns:\n        Dict[str, str]: 헬스체크 결과\n    \"\"\"\n    try:\n        # 간단한 서비스 동작 테스트\n        stats = await service.get_user_stats()\n        \n        return {\n            \"status\": \"healthy\",\n            \"message\": \"사용자 서비스 정상 동작\",\n            \"timestamp\": str(datetime.now()),\n            \"total_users\": str(stats.get(\"total_users\", 0))\n        }\n        \n    except Exception as e:\n        logger.error(f\"❌ 사용자 서비스 헬스체크 실패: {e}\")\n        return {\n            \"status\": \"unhealthy\",\n            \"message\": f\"사용자 서비스 오류: {str(e)}\",\n            \"timestamp\": str(datetime.now())\n        }\n\n\n# 에러 핸들러 (선택사항)\n@router.exception_handler(HTTPException)\nasync def http_exception_handler(request, exc):\n    \"\"\"\n    HTTP 예외 처리기\n    \n    일관된 에러 응답 형식을 제공합니다.\n    \"\"\"\n    return JSONResponse(\n        status_code=exc.status_code,\n        content={\n            \"success\": False,\n            \"message\": exc.detail,\n            \"error_code\": exc.status_code,\n            \"timestamp\": str(datetime.now())\n        }\n    )"