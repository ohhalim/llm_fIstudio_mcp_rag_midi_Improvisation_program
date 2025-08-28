"""
routers/events.py - 이벤트 관련 API 라우터

이 파일에서 배울 수 있는 개념들:
1. 이벤트 기반 API 설계
2. Kafka 메시지 발행 API
3. 실시간 이벤트 처리
4. 백그라운드 태스크
5. WebSocket을 통한 실시간 통신 (선택사항)
6. 이벤트 추적 및 모니터링
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json
from models import (
    EventBase, EventType, KafkaMessage, APIResponse
)
from services.kafka_service import kafka_service, publish_user_event, publish_system_event


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(
    prefix="/events",  # 모든 경로에 /events 접두사 추가
    tags=["events"],   # OpenAPI 문서에서 그룹화
    responses={
        422: {"description": "입력 데이터 검증 실패"},
        500: {"description": "이벤트 처리 실패"}
    }
)


# 의존성 함수들
async def get_kafka_service():
    """
    Kafka 서비스 의존성
    
    의존성 주입 패턴을 사용하여 Kafka 서비스를 주입받습니다.
    """
    return kafka_service


def validate_topic_name(topic: str) -> str:
    """
    토픽 이름 검증 의존성
    
    Args:
        topic (str): 검증할 토픽 이름
        
    Returns:
        str: 검증된 토픽 이름
        
    Raises:
        HTTPException: 토픽 이름이 유효하지 않을 때
    """
    if not topic or len(topic) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="토픽 이름은 최소 3자 이상이어야 합니다"
        )
    
    if not topic.replace('_', '').replace('-', '').isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="토픽 이름은 영문자, 숫자, 하이픈, 언더스코어만 포함할 수 있습니다"
        )
    
    return topic


# 이벤트 발행 API들

@router.post(
    "/publish",
    response_model=APIResponse,
    summary="일반 이벤트 발행",
    description="지정된 토픽으로 커스텀 이벤트를 발행합니다.",
    status_code=status.HTTP_201_CREATED
)
async def publish_event(
    topic: str = Query(..., description="대상 토픽 이름"),
    event: EventBase = ...,
    background_tasks: BackgroundTasks = ...,
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    일반 이벤트 발행 엔드포인트
    
    Args:
        topic (str): 이벤트를 발행할 토픽
        event (EventBase): 발행할 이벤트 데이터
        background_tasks (BackgroundTasks): 백그라운드 처리
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 발행 결과
        
    백그라운드 태스크:
        비동기적으로 이벤트를 처리하여 API 응답 속도를 향상시킵니다.
    """
    try:
        # 토픽 이름 검증
        validated_topic = validate_topic_name(topic)
        
        logger.info(f"📤 이벤트 발행 요청: {validated_topic} - {event.event_type}")
        
        # 이벤트 메타데이터 추가
        event.timestamp = datetime.now()
        
        # 백그라운드에서 이벤트 발행 (논블로킹)
        def publish_in_background():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(service.send_event(validated_topic, event))
                if success:
                    logger.info(f"✅ 백그라운드 이벤트 발행 성공: {validated_topic}")
                else:
                    logger.error(f"❌ 백그라운드 이벤트 발행 실패: {validated_topic}")
            finally:
                loop.close()
        
        background_tasks.add_task(publish_in_background)
        
        # 즉시 응답 반환 (실제 발행은 백그라운드에서)
        return APIResponse(
            success=True,
            message=f"이벤트가 {validated_topic} 토픽으로 발행 요청되었습니다",
            data={
                "topic": validated_topic,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 이벤트 발행 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이벤트 발행 중 오류가 발생했습니다"
        )


@router.post(
    "/publish/sync",
    response_model=APIResponse,
    summary="동기 이벤트 발행",
    description="이벤트 발행을 동기적으로 처리하고 결과를 확인합니다.",
    status_code=status.HTTP_201_CREATED
)
async def publish_event_sync(
    topic: str = Query(..., description="대상 토픽 이름"),
    event: EventBase = ...,
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    동기 이벤트 발행 엔드포인트
    
    백그라운드 처리 대신 즉시 발행하고 결과를 반환합니다.
    중요한 이벤트나 결과 확인이 필요한 경우 사용합니다.
    
    Args:
        topic (str): 이벤트를 발행할 토픽
        event (EventBase): 발행할 이벤트 데이터
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 발행 결과
    """
    try:
        # 토픽 이름 검증
        validated_topic = validate_topic_name(topic)
        
        logger.info(f"📤 동기 이벤트 발행 요청: {validated_topic} - {event.event_type}")
        
        # 이벤트 메타데이터 추가
        event.timestamp = datetime.now()
        
        # 동기적으로 이벤트 발행
        success = await service.send_event(validated_topic, event)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="이벤트 발행에 실패했습니다"
            )
        
        logger.info(f"✅ 동기 이벤트 발행 성공: {validated_topic}")
        
        return APIResponse(
            success=True,
            message=f"이벤트가 {validated_topic} 토픽으로 성공적으로 발행되었습니다",
            data={
                "topic": validated_topic,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat(),
                "published": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 동기 이벤트 발행 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="동기 이벤트 발행 중 오류가 발생했습니다"
        )


@router.post(
    "/user-events",
    response_model=APIResponse,
    summary="사용자 이벤트 발행",
    description="사용자 관련 특화된 이벤트를 발행합니다.",
    status_code=status.HTTP_201_CREATED
)
async def publish_user_event_api(
    event_type: EventType = Query(..., description="사용자 이벤트 타입"),
    user_id: int = Query(..., description="대상 사용자 ID"),
    event_data: Optional[Dict[str, Any]] = None,
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    사용자 이벤트 발행 엔드포인트
    
    사용자 관련 이벤트를 user_events 토픽으로 발행합니다.
    메시지 키로 user_id를 사용하여 순서를 보장합니다.
    
    Args:
        event_type (EventType): 사용자 이벤트 타입
        user_id (int): 대상 사용자 ID
        event_data (Optional[Dict[str, Any]]): 추가 이벤트 데이터
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 발행 결과
    """
    try:
        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="사용자 ID는 양수여야 합니다"
            )
        
        logger.info(f"👤 사용자 이벤트 발행: {event_type} (사용자: {user_id})")
        
        # 편의 함수 사용 (사용자 이벤트 특화)
        success = await publish_user_event(
            event_type=event_type,
            user_id=user_id,
            data=event_data or {}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 이벤트 발행에 실패했습니다"
            )
        
        logger.info(f"✅ 사용자 이벤트 발행 성공: {event_type} (사용자: {user_id})")
        
        return APIResponse(
            success=True,
            message=f"사용자 이벤트 {event_type}가 성공적으로 발행되었습니다",
            data={
                "event_type": event_type,
                "user_id": user_id,
                "topic": "user_events",
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사용자 이벤트 발행 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 이벤트 발행 중 오류가 발생했습니다"
        )


@router.post(
    "/system-events",
    response_model=APIResponse,
    summary="시스템 이벤트 발행",
    description="시스템 레벨 이벤트를 발행합니다.",
    status_code=status.HTTP_201_CREATED
)
async def publish_system_event_api(
    event_type: str = Query(..., description="시스템 이벤트 타입"),
    event_data: Dict[str, Any] = ...,
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    시스템 이벤트 발행 엔드포인트
    
    시스템 레벨의 이벤트를 system_events 토픽으로 발행합니다.
    
    Args:
        event_type (str): 시스템 이벤트 타입
        event_data (Dict[str, Any]): 이벤트 데이터
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 발행 결과
    """
    try:
        logger.info(f"🔧 시스템 이벤트 발행: {event_type}")
        
        # 편의 함수 사용 (시스템 이벤트 특화)
        success = await publish_system_event(
            event_type=event_type,
            data=event_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="시스템 이벤트 발행에 실패했습니다"
            )
        
        logger.info(f"✅ 시스템 이벤트 발행 성공: {event_type}")
        
        return APIResponse(
            success=True,
            message=f"시스템 이벤트 {event_type}가 성공적으로 발행되었습니다",
            data={
                "event_type": event_type,
                "topic": "system_events",
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 시스템 이벤트 발행 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="시스템 이벤트 발행 중 오류가 발생했습니다"
        )


# Kafka 관리 API들

@router.get(
    "/topics",
    response_model=APIResponse,
    summary="토픽 목록 조회",
    description="사용 가능한 Kafka 토픽 목록을 조회합니다."
)
async def list_topics(
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    토픽 목록 조회 엔드포인트
    
    Kafka 클러스터에 존재하는 토픽 목록을 반환합니다.
    
    Args:
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 토픽 목록이 포함된 응답
    """
    try:
        logger.info("📋 토픽 목록 조회 요청")
        
        topics = await service.list_topics()
        
        logger.info(f"✅ 토픽 목록 조회 성공: {len(topics)}개")
        
        return APIResponse(
            success=True,
            message="토픽 목록 조회 성공",
            data={
                "topics": topics,
                "count": len(topics)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 토픽 목록 조회 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토픽 목록 조회 중 오류가 발생했습니다"
        )


@router.post(
    "/topics",
    response_model=APIResponse,
    summary="토픽 생성",
    description="새로운 Kafka 토픽을 생성합니다.",
    status_code=status.HTTP_201_CREATED
)
async def create_topic(
    topic_name: str = Query(..., description="생성할 토픽 이름"),
    num_partitions: int = Query(3, ge=1, le=50, description="파티션 수 (1-50)"),
    replication_factor: int = Query(1, ge=1, le=5, description="복제본 수 (1-5)"),
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    토픽 생성 엔드포인트
    
    새로운 Kafka 토픽을 생성합니다.
    파티션 수는 병렬 처리 수준을, 복제본 수는 데이터 안정성을 결정합니다.
    
    Args:
        topic_name (str): 생성할 토픽 이름
        num_partitions (int): 파티션 수
        replication_factor (int): 복제본 수
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 토픽 생성 결과
    """
    try:
        # 토픽 이름 검증
        validated_topic = validate_topic_name(topic_name)
        
        logger.info(f"🆕 토픽 생성 요청: {validated_topic} (파티션: {num_partitions}, 복제본: {replication_factor})")
        
        success = await service.create_topic(
            topic_name=validated_topic,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="토픽 생성에 실패했습니다"
            )
        
        logger.info(f"✅ 토픽 생성 성공: {validated_topic}")
        
        return APIResponse(
            success=True,
            message=f"토픽 {validated_topic}가 성공적으로 생성되었습니다",
            data={
                "topic_name": validated_topic,
                "num_partitions": num_partitions,
                "replication_factor": replication_factor
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 토픽 생성 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토픽 생성 중 오류가 발생했습니다"
        )


@router.delete(
    "/topics/{topic_name}",
    response_model=APIResponse,
    summary="토픽 삭제",
    description="지정된 Kafka 토픽을 삭제합니다."
)
async def delete_topic(
    topic_name: str,
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    토픽 삭제 엔드포인트
    
    ⚠️ 주의: 토픽을 삭제하면 해당 토픽의 모든 메시지가 삭제됩니다.
    
    Args:
        topic_name (str): 삭제할 토픽 이름
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 토픽 삭제 결과
    """
    try:
        # 토픽 이름 검증
        validated_topic = validate_topic_name(topic_name)
        
        logger.info(f"🗑️ 토픽 삭제 요청: {validated_topic}")
        
        # 중요한 토픽 보호
        protected_topics = ['user_events', 'system_events']
        if validated_topic in protected_topics:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"보호된 토픽 {validated_topic}는 삭제할 수 없습니다"
            )
        
        success = await service.delete_topic(validated_topic)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="토픽 삭제에 실패했습니다"
            )
        
        logger.info(f"✅ 토픽 삭제 성공: {validated_topic}")
        
        return APIResponse(
            success=True,
            message=f"토픽 {validated_topic}가 성공적으로 삭제되었습니다",
            data={
                "deleted_topic": validated_topic
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 토픽 삭제 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토픽 삭제 중 오류가 발생했습니다"
        )


# 모니터링 및 헬스체크

@router.get(
    "/health",
    summary="이벤트 서비스 헬스체크",
    description="이벤트 서비스와 Kafka 연결 상태를 확인합니다."
)
async def health_check(
    service: Any = Depends(get_kafka_service)
) -> Dict[str, str]:
    """
    이벤트 서비스 헬스체크 엔드포인트
    
    Kafka 클러스터 연결 상태와 기본 기능을 확인합니다.
    
    Args:
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        Dict[str, str]: 헬스체크 결과
    """
    try:
        # Kafka 헬스체크
        health_result = await service.health_check()
        
        return {
            **health_result,
            "service": "events",
            "kafka_status": health_result.get("status", "unknown")
        }
        
    except Exception as e:
        logger.error(f"❌ 이벤트 서비스 헬스체크 실패: {e}")
        return {
            "status": "unhealthy",
            "message": f"이벤트 서비스 오류: {str(e)}",
            "service": "events",
            "timestamp": datetime.now().isoformat()
        }


# 실시간 이벤트 스트림 (WebSocket - 선택사항)
# 실제 환경에서는 WebSocket을 사용하여 실시간 이벤트 스트림을 제공할 수 있습니다.

@router.get(
    "/stats",
    response_model=APIResponse,
    summary="이벤트 통계",
    description="이벤트 처리 통계를 조회합니다."
)
async def get_event_stats(
    service: Any = Depends(get_kafka_service)
) -> APIResponse:
    """
    이벤트 통계 조회 엔드포인트
    
    실제 환경에서는 메트릭 수집 시스템과 연동하여
    더 상세한 통계를 제공할 수 있습니다.
    
    Args:
        service: 의존성으로 주입받은 Kafka 서비스
        
    Returns:
        APIResponse: 이벤트 통계 정보
    """
    try:
        logger.info("📊 이벤트 통계 조회 요청")
        
        # 토픽 목록 조회
        topics = await service.list_topics()
        
        # 간단한 통계 정보 (실제로는 더 상세한 메트릭 필요)
        stats = {
            "total_topics": len(topics),
            "active_topics": [t for t in topics if not t.startswith('_')],  # 시스템 토픽 제외
            "system_topics": [t for t in topics if t.startswith('_')],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ 이벤트 통계 조회 성공")
        
        return APIResponse(
            success=True,
            message="이벤트 통계 조회 성공",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"❌ 이벤트 통계 조회 중 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이벤트 통계 조회 중 오류가 발생했습니다"
        )