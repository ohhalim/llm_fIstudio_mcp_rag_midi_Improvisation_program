"""
services/kafka_service.py - Apache Kafka 메시징 서비스

이 파일에서 배울 수 있는 개념들:
1. Kafka Producer/Consumer 패턴
2. 이벤트 기반 아키텍처 (Event-Driven Architecture)
3. 메시지 직렬화/역직렬화
4. 에러 핸들링과 재시도 로직
5. 비동기 메시지 처리
6. 백프레셔(Backpressure) 관리
"""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType, NewTopic
from kafka.errors import KafkaError, KafkaTimeoutError
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from config import settings
from models import EventBase, KafkaMessage, EventType
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaService:
    """
    Kafka 메시징 서비스 클래스
    
    이벤트 발행(Producer)과 구독(Consumer) 기능을 제공합니다.
    마이크로서비스 간 비동기 통신의 핵심 역할을 담당합니다.
    """
    
    def __init__(self):
        """
        Kafka 서비스 초기화
        """
        self.bootstrap_servers = settings.kafka_bootstrap_servers.split(',')
        self.producer = None
        self.admin_client = None
        self.consumers = {}  # 토픽별 컨슈머 저장
        self.executor = ThreadPoolExecutor(max_workers=4)  # 비동기 실행용
        
        # Producer 초기화
        self._init_producer()
        
        # Admin 클라이언트 초기화
        self._init_admin_client()
        
        logger.info("✅ Kafka 서비스 초기화 완료")
    
    def _init_producer(self):
        """
        Kafka Producer 초기화
        
        Producer는 메시지를 Kafka 토픽으로 전송하는 역할을 합니다.
        """
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                
                # 메시지 직렬화 설정
                value_serializer=lambda v: json.dumps(
                    v, 
                    default=self._json_serializer,
                    ensure_ascii=False
                ).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None,
                
                # 성능 및 신뢰성 설정
                acks='all',  # 모든 복제본에서 확인받기 (최고 신뢰성)
                retries=3,   # 실패 시 3번 재시도
                max_in_flight_requests_per_connection=1,  # 순서 보장
                
                # 배치 및 압축 설정 (성능 최적화)
                batch_size=16384,  # 16KB 배치
                linger_ms=10,      # 10ms 대기 후 전송
                compression_type='gzip',  # GZIP 압축
                
                # 타임아웃 설정
                request_timeout_ms=30000,  # 30초
                delivery_timeout_ms=120000,  # 2분
                
                # 에러 콜백
                on_send_error=self._on_send_error
            )
            logger.info("✅ Kafka Producer 초기화 성공")
            
        except Exception as e:
            logger.error(f"❌ Kafka Producer 초기화 실패: {e}")
            raise
    
    def _init_admin_client(self):
        """
        Kafka Admin 클라이언트 초기화
        
        토픽 관리, 설정 변경 등의 관리 작업을 수행합니다.
        """
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='fastapi_admin',
                request_timeout_ms=30000
            )
            logger.info("✅ Kafka Admin 클라이언트 초기화 성공")
            
        except Exception as e:
            logger.error(f"❌ Kafka Admin 클라이언트 초기화 실패: {e}")
            self.admin_client = None
    
    # Producer 메서드들
    async def send_event(self, topic: str, event: EventBase, key: Optional[str] = None) -> bool:
        """
        이벤트 발행
        
        Args:
            topic (str): 대상 토픽
            event (EventBase): 발행할 이벤트
            key (Optional[str]): 메시지 키 (파티션 결정에 사용)
            
        Returns:
            bool: 전송 성공 여부
            
        메시지 키(key)는 같은 키를 가진 메시지들이 같은 파티션으로 가도록 보장합니다.
        순서가 중요한 이벤트(예: 사용자별 이벤트)에서 사용합니다.
        """
        try:
            # 이벤트 데이터 준비
            event_data = event.dict() if hasattr(event, 'dict') else event
            
            # 메타데이터 추가
            event_data['_metadata'] = {
                'producer': 'fastapi_service',
                'sent_at': datetime.now().isoformat(),
                'topic': topic
            }
            
            # 비동기 전송 (블로킹하지 않음)
            future = self.producer.send(
                topic=topic,
                value=event_data,
                key=key,
                headers=[
                    ('content-type', b'application/json'),
                    ('event-type', event.event_type.encode('utf-8'))
                ]
            )
            
            # 전송 완료 대기 (타임아웃 포함)
            record_metadata = future.get(timeout=30)
            
            logger.info(
                f"✅ 이벤트 전송 성공: {topic} "
                f"(파티션: {record_metadata.partition}, "
                f"오프셋: {record_metadata.offset})"
            )
            
            return True
            
        except KafkaTimeoutError:
            logger.error(f"❌ Kafka 전송 타임아웃: {topic}")
            return False
        except KafkaError as e:
            logger.error(f"❌ Kafka 전송 오류 ({topic}): {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 이벤트 전송 중 예상치 못한 오류 ({topic}): {e}")
            return False
    
    async def send_message(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """
        일반 메시지 전송 (이벤트가 아닌 경우)
        """
        try:
            future = self.producer.send(
                topic=topic,
                value=message,
                key=key
            )
            
            record_metadata = future.get(timeout=30)
            
            logger.info(
                f"✅ 메시지 전송 성공: {topic} "
                f"(파티션: {record_metadata.partition}, 오프셋: {record_metadata.offset})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 메시지 전송 오류 ({topic}): {e}")
            return False
    
    def flush(self, timeout: int = 30):
        """
        Producer 버퍼에 있는 모든 메시지 즉시 전송
        
        애플리케이션 종료 시나 중요한 메시지 전송 후 호출합니다.
        """
        try:
            self.producer.flush(timeout=timeout)
            logger.info("✅ Kafka Producer flush 완료")
        except Exception as e:
            logger.error(f"❌ Kafka Producer flush 오류: {e}")
    
    # Consumer 메서드들
    def create_consumer(self, 
                       topics: List[str], 
                       group_id: str = None,
                       auto_offset_reset: str = 'latest') -> KafkaConsumer:
        """
        Kafka Consumer 생성
        
        Args:
            topics (List[str]): 구독할 토픽 목록
            group_id (str): 컨슈머 그룹 ID
            auto_offset_reset (str): 오프셋 리셋 정책 (earliest/latest)
            
        Returns:
            KafkaConsumer: 생성된 컨슈머
            
        컨슈머 그룹:
        - 같은 그룹의 컨슈머들은 메시지를 분산해서 처리
        - 다른 그룹의 컨슈머들은 모든 메시지를 각각 받음
        """
        try:
            if group_id is None:
                group_id = settings.kafka_group_id
            
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                
                # 메시지 역직렬화
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                
                # 오프셋 관리
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,  # 5초마다 오프셋 커밋
                
                # 세션 관리
                session_timeout_ms=30000,  # 30초
                heartbeat_interval_ms=3000,  # 3초
                
                # 성능 설정
                fetch_max_wait_ms=500,  # 최대 500ms 대기
                max_poll_records=500,   # 한 번에 최대 500개 메시지
                
                # 네트워크 설정
                request_timeout_ms=40000,  # 40초
                retry_backoff_ms=100
            )
            
            logger.info(f"✅ Kafka Consumer 생성: {topics} (그룹: {group_id})")
            return consumer
            
        except Exception as e:
            logger.error(f"❌ Kafka Consumer 생성 실패: {e}")
            raise
    
    async def consume_messages(self, 
                              topics: List[str], 
                              message_handler: Callable,
                              group_id: str = None) -> None:
        """
        메시지 비동기 소비
        
        Args:
            topics (List[str]): 구독할 토픽 목록
            message_handler (Callable): 메시지 처리 함수
            group_id (str): 컨슈머 그룹 ID
            
        이 메서드는 백그라운드에서 계속 실행되며 메시지를 처리합니다.
        """
        def _consume_loop():
            consumer = self.create_consumer(topics, group_id)
            try:
                logger.info(f"🔄 메시지 소비 시작: {topics}")
                
                for message in consumer:
                    try:
                        # 메시지 정보 로깅
                        logger.info(
                            f"📨 메시지 수신: {message.topic} "
                            f"(파티션: {message.partition}, 오프셋: {message.offset})"
                        )
                        
                        # 메시지 처리
                        asyncio.run(message_handler(message))
                        
                    except Exception as e:
                        logger.error(f"❌ 메시지 처리 오류: {e}")
                        # 에러가 발생해도 계속 처리 (장애 격리)
                        continue
                        
            except KeyboardInterrupt:
                logger.info("⏹️ 메시지 소비 중단")
            except Exception as e:
                logger.error(f"❌ 메시지 소비 중 오류: {e}")
            finally:
                consumer.close()
                logger.info("✅ Consumer 연결 종료")
        
        # 별도 스레드에서 실행 (비동기 처리)
        future = self.executor.submit(_consume_loop)
        return future
    
    # 토픽 관리
    async def create_topic(self, topic_name: str, num_partitions: int = 3, replication_factor: int = 1) -> bool:
        """
        토픽 생성
        
        Args:
            topic_name (str): 생성할 토픽 이름
            num_partitions (int): 파티션 수 (병렬 처리 수준 결정)
            replication_factor (int): 복제본 수 (장애 대응)
            
        Returns:
            bool: 생성 성공 여부
        """
        if not self.admin_client:
            logger.error("❌ Admin 클라이언트가 초기화되지 않았습니다")
            return False
        
        try:
            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                topic_configs={
                    'retention.ms': '604800000',  # 7일간 보관
                    'compression.type': 'gzip',
                    'cleanup.policy': 'delete'
                }
            )
            
            # 토픽 생성 요청
            future = self.admin_client.create_topics([topic], validate_only=False)
            
            # 결과 대기
            for topic_name, future in future.items():
                future.result()  # 예외 발생 시 여기서 캐치됨
            
            logger.info(f"✅ 토픽 생성 성공: {topic_name}")
            return True
            
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"ℹ️ 토픽이 이미 존재합니다: {topic_name}")
                return True
            else:
                logger.error(f"❌ 토픽 생성 실패 ({topic_name}): {e}")
                return False
    
    async def list_topics(self) -> List[str]:
        """
        토픽 목록 조회
        """
        if not self.admin_client:
            return []
        
        try:
            metadata = self.admin_client.list_topics()
            topics = list(metadata.topics.keys())
            logger.info(f"📋 토픽 목록: {topics}")
            return topics
        except Exception as e:
            logger.error(f"❌ 토픽 목록 조회 실패: {e}")
            return []
    
    async def delete_topic(self, topic_name: str) -> bool:
        """
        토픽 삭제
        """
        if not self.admin_client:
            return False
        
        try:
            future = self.admin_client.delete_topics([topic_name])
            for topic_name, future in future.items():
                future.result()
            
            logger.info(f"✅ 토픽 삭제 성공: {topic_name}")
            return True
        except Exception as e:
            logger.error(f"❌ 토픽 삭제 실패 ({topic_name}): {e}")
            return False
    
    # 헬스체크 및 모니터링
    async def health_check(self) -> Dict[str, str]:
        """
        Kafka 연결 상태 확인
        """
        try:
            # Producer 상태 확인
            if not self.producer:
                return {
                    "status": "unhealthy",
                    "message": "Producer가 초기화되지 않았습니다",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 클러스터 메타데이터 조회로 연결 상태 확인
            metadata = self.producer.list_topics(timeout=5)
            
            if metadata:
                broker_count = len(self.producer.cluster.brokers())
                return {
                    "status": "healthy",
                    "message": f"Kafka 연결 정상 (브로커 수: {broker_count})",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "메타데이터 조회 실패",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Kafka 오류: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    # 유틸리티 메서드들
    def _json_serializer(self, obj):
        """JSON 직렬화용 커스텀 시리얼라이저"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):  # Pydantic 모델
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _on_send_error(self, exception):
        """Producer 전송 실패 시 호출되는 콜백"""
        logger.error(f"❌ Kafka Producer 전송 오류: {exception}")
    
    def close(self):
        """
        모든 연결 종료
        
        애플리케이션 종료 시 호출
        """
        try:
            if self.producer:
                self.flush()  # 버퍼에 있는 메시지 전송
                self.producer.close()
                logger.info("✅ Kafka Producer 연결 종료")
            
            if self.admin_client:
                self.admin_client.close()
                logger.info("✅ Kafka Admin 클라이언트 연결 종료")
            
            # 스레드 풀 종료
            self.executor.shutdown(wait=True)
            
        except Exception as e:
            logger.error(f"❌ Kafka 연결 종료 중 오류: {e}")


# 싱글톤 인스턴스 생성
kafka_service = KafkaService()


# 편의 함수들
async def publish_user_event(event_type: EventType, user_id: int, data: Dict[str, Any] = None) -> bool:
    """사용자 이벤트 발행 편의 함수"""
    event = EventBase(
        event_type=event_type,
        user_id=user_id,
        data=data or {}
    )
    return await kafka_service.send_event("user_events", event, key=str(user_id))


async def publish_system_event(event_type: str, data: Dict[str, Any]) -> bool:
    """시스템 이벤트 발행 편의 함수"""
    event = EventBase(
        event_type=event_type,
        data=data
    )
    return await kafka_service.send_event("system_events", event)


if __name__ == "__main__":
    """
    Kafka 서비스 테스트 코드
    """
    import asyncio
    
    async def test_kafka_service():
        print("Kafka 서비스 테스트 시작...")
        
        # 토픽 생성 테스트
        await kafka_service.create_topic("test_topic", num_partitions=2)
        
        # 토픽 목록 조회
        topics = await kafka_service.list_topics()
        print(f"사용 가능한 토픽: {topics}")
        
        # 이벤트 발행 테스트
        test_event = EventBase(
            event_type=EventType.USER_CREATED,
            user_id=123,
            data={"email": "test@example.com", "name": "테스트 사용자"}
        )
        
        success = await kafka_service.send_event("test_topic", test_event)
        print(f"이벤트 발행: {success}")
        
        # 헬스체크
        health = await kafka_service.health_check()
        print(f"헬스체크: {health}")
    
    # 테스트 실행
    asyncio.run(test_kafka_service())