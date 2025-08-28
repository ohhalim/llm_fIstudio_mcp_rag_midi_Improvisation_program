"""
consumers/user_consumer.py - 사용자 이벤트 컨슈머

이 파일에서 배울 수 있는 개념들:
1. Kafka Consumer 패턴
2. 이벤트 기반 처리 (Event-Driven Processing)
3. 에러 처리와 재시도 로직
4. 백그라운드 프로세싱
5. 로깅과 모니터링
6. graceful shutdown 처리
"""

import asyncio
import signal
import sys
import json
import logging
from typing import Dict, Any
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from services.kafka_service import kafka_service
from services.redis_service import redis_service
from models import EventType
import time


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('consumer.log'),  # 로그 파일에 저장
        logging.StreamHandler(sys.stdout)      # 콘솔에도 출력
    ]
)
logger = logging.getLogger(__name__)


class UserEventConsumer:
    """
    사용자 이벤트 처리를 위한 Kafka Consumer 클래스
    
    사용자 관련 이벤트를 구독하고 처리하는 역할을 담당합니다.
    - 이벤트 수신 및 파싱
    - 비즈니스 로직 처리
    - 에러 핸들링 및 재시도
    - 메트릭 수집
    """
    
    def __init__(self, group_id: str = "user_event_processor"):
        """
        사용자 이벤트 컨슈머 초기화
        
        Args:
            group_id (str): 컨슈머 그룹 ID
        """
        self.group_id = group_id
        self.consumer = None
        self.running = False
        self.processed_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        # 처리할 토픽 목록
        self.topics = ['user_events']
        
        # 이벤트 처리기 매핑
        self.event_handlers = {
            EventType.USER_CREATED: self._handle_user_created,
            EventType.USER_UPDATED: self._handle_user_updated,
            EventType.USER_DELETED: self._handle_user_deleted,
            EventType.USER_LOGIN: self._handle_user_login,
            EventType.USER_LOGOUT: self._handle_user_logout
        }
        
        logger.info(f"✅ 사용자 이벤트 컨슈머 초기화 완료 (그룹: {group_id})")
    
    def create_consumer(self) -> KafkaConsumer:
        """
        Kafka Consumer 인스턴스 생성
        
        Returns:
            KafkaConsumer: 구성된 컨슈머 인스턴스
        """
        try:
            consumer = kafka_service.create_consumer(
                topics=self.topics,
                group_id=self.group_id,
                auto_offset_reset='earliest'  # 처음부터 모든 메시지 처리
            )
            
            logger.info(f"🔄 Kafka Consumer 생성: {self.topics} (그룹: {self.group_id})")
            return consumer
            
        except Exception as e:\n            logger.error(f\"❌ Kafka Consumer 생성 실패: {e}\")\n            raise\n    \n    async def start(self):\n        \"\"\"\n        컨슈머 시작\n        \n        메인 이벤트 루프를 시작하고 메시지를 처리합니다.\n        Graceful shutdown을 위한 시그널 핸들러도 설정합니다.\n        \"\"\"\n        try:\n            # 시그널 핸들러 설정 (Ctrl+C 처리)\n            signal.signal(signal.SIGINT, self._signal_handler)\n            signal.signal(signal.SIGTERM, self._signal_handler)\n            \n            # Consumer 생성\n            self.consumer = self.create_consumer()\n            self.running = True\n            \n            logger.info(\"🚀 사용자 이벤트 컨슈머 시작\")\n            logger.info(f\"📋 구독 토픽: {self.topics}\")\n            logger.info(f\"👥 컨슈머 그룹: {self.group_id}\")\n            \n            # 메인 처리 루프\n            await self._process_messages()\n            \n        except KeyboardInterrupt:\n            logger.info(\"⏹️ 사용자 중단 신호 수신\")\n        except Exception as e:\n            logger.error(f\"❌ 컨슈머 실행 중 오류: {e}\")\n            raise\n        finally:\n            await self._shutdown()\n    \n    async def _process_messages(self):\n        \"\"\"\n        메시지 처리 메인 루프\n        \n        Kafka에서 메시지를 수신하고 적절한 핸들러로 전달합니다.\n        \"\"\"\n        logger.info(\"🔄 메시지 처리 루프 시작\")\n        \n        try:\n            # 메시지 폴링 및 처리\n            for message in self.consumer:\n                if not self.running:\n                    logger.info(\"⏹️ 컨슈머 중단 플래그 확인됨\")\n                    break\n                \n                try:\n                    # 메시지 처리\n                    await self._handle_message(message)\n                    \n                    # 통계 업데이트\n                    self.processed_count += 1\n                    \n                    # 주기적으로 통계 출력 (100개마다)\n                    if self.processed_count % 100 == 0:\n                        await self._log_stats()\n                    \n                except Exception as e:\n                    logger.error(f\"❌ 메시지 처리 중 오류: {e}\")\n                    self.error_count += 1\n                    \n                    # 에러가 너무 많으면 잠시 대기\n                    if self.error_count > 10:\n                        logger.warning(\"⚠️ 에러가 많이 발생하여 5초 대기\")\n                        await asyncio.sleep(5)\n                        self.error_count = 0  # 에러 카운트 리셋\n        \n        except Exception as e:\n            logger.error(f\"❌ 메시지 처리 루프 중 오류: {e}\")\n            raise\n    \n    async def _handle_message(self, message):\n        \"\"\"\n        개별 메시지 처리\n        \n        Args:\n            message: Kafka 메시지\n        \"\"\"\n        try:\n            # 메시지 정보 로깅\n            logger.info(\n                f\"📨 메시지 수신: {message.topic} \"\n                f\"(파티션: {message.partition}, 오프셋: {message.offset})\"\n            )\n            \n            # 메시지 데이터 파싱\n            event_data = message.value\n            event_type = event_data.get('event_type')\n            user_id = event_data.get('user_id')\n            \n            # 메시지 검증\n            if not event_type:\n                logger.warning(f\"⚠️ 이벤트 타입이 없는 메시지: {message.offset}\")\n                return\n            \n            # 헤더 정보 추출 (있는 경우)\n            headers = dict(message.headers) if message.headers else {}\n            \n            # 처리 시작 로그\n            logger.info(f\"🔄 이벤트 처리 시작: {event_type} (사용자: {user_id})\")\n            \n            # 적절한 핸들러 찾기 및 실행\n            handler = self.event_handlers.get(event_type)\n            \n            if handler:\n                await handler(event_data, headers)\n                logger.info(f\"✅ 이벤트 처리 완료: {event_type} (사용자: {user_id})\")\n            else:\n                logger.warning(f\"⚠️ 알 수 없는 이벤트 타입: {event_type}\")\n                await self._handle_unknown_event(event_data)\n        \n        except json.JSONDecodeError as e:\n            logger.error(f\"❌ JSON 파싱 오류: {e}\")\n        except Exception as e:\n            logger.error(f\"❌ 메시지 처리 중 예상치 못한 오류: {e}\")\n            raise\n    \n    # 이벤트 핸들러들\n    \n    async def _handle_user_created(self, event_data: Dict[str, Any], headers: Dict[str, Any]):\n        \"\"\"\n        사용자 생성 이벤트 처리\n        \n        사용자가 새로 생성되었을 때의 후속 처리를 수행합니다:\n        - 환영 이메일 발송\n        - 초기 설정 생성\n        - 로그 기록\n        \"\"\"\n        try:\n            user_id = event_data.get('user_id')\n            user_data = event_data.get('data', {})\n            \n            logger.info(f\"👤 새 사용자 생성 처리: {user_id}\")\n            \n            # 1. 환영 메시지를 캐시에 저장 (예시)\n            welcome_message = {\n                \"message\": f\"{user_data.get('name', '사용자')}님, 환영합니다!\",\n                \"created_at\": datetime.now().isoformat(),\n                \"read\": False\n            }\n            \n            cache_key = f\"welcome_message:{user_id}\"\n            await redis_service.set_cache(cache_key, welcome_message, expire=86400)  # 24시간\n            \n            # 2. 사용자 생성 로그 기록\n            await self._log_user_activity(\n                user_id=user_id,\n                activity=\"user_created\",\n                details=user_data\n            )\n            \n            # 3. 실제 환경에서는 이메일 서비스 호출\n            await self._send_welcome_email(user_data.get('email'), user_data.get('name'))\n            \n            logger.info(f\"✅ 사용자 생성 후속 처리 완료: {user_id}\")\n            \n        except Exception as e:\n            logger.error(f\"❌ 사용자 생성 이벤트 처리 중 오류: {e}\")\n            raise\n    \n    async def _handle_user_updated(self, event_data: Dict[str, Any], headers: Dict[str, Any]):\n        \"\"\"\n        사용자 정보 수정 이벤트 처리\n        \"\"\"\n        try:\n            user_id = event_data.get('user_id')\n            changed_fields = event_data.get('data', {}).get('changed_fields', [])\n            \n            logger.info(f\"🔄 사용자 정보 수정 처리: {user_id} (변경: {changed_fields})\")\n            \n            # 중요한 필드 변경 시 추가 처리\n            if 'email' in changed_fields:\n                # 이메일 변경 시 인증 이메일 발송\n                logger.info(f\"📧 이메일 변경 감지: {user_id} - 인증 이메일 발송 필요\")\n                # await self._send_email_verification(user_id)\n            \n            if 'status' in changed_fields:\n                # 상태 변경 시 알림\n                logger.info(f\"🔔 사용자 상태 변경: {user_id}\")\n            \n            # 사용자 수정 로그 기록\n            await self._log_user_activity(\n                user_id=user_id,\n                activity=\"user_updated\",\n                details={\"changed_fields\": changed_fields}\n            )\n            \n        except Exception as e:\n            logger.error(f\"❌ 사용자 수정 이벤트 처리 중 오류: {e}\")\n            raise\n    \n    async def _handle_user_deleted(self, event_data: Dict[str, Any], headers: Dict[str, Any]):\n        \"\"\"\n        사용자 삭제 이벤트 처리\n        \"\"\"\n        try:\n            user_id = event_data.get('user_id')\n            \n            logger.info(f\"🗑️ 사용자 삭제 처리: {user_id}\")\n            \n            # 1. 관련 캐시 데이터 삭제\n            await redis_service.delete_user_cache(user_id)\n            await redis_service.delete_cache(f\"welcome_message:{user_id}\")\n            \n            # 2. 사용자 활동 로그에 삭제 기록\n            await self._log_user_activity(\n                user_id=user_id,\n                activity=\"user_deleted\",\n                details={\"deleted_at\": datetime.now().isoformat()}\n            )\n            \n            # 3. 실제 환경에서는 관련 데이터 정리\n            # - 사용자 파일 삭제\n            # - 관련 서비스 알림\n            # - 데이터 보존 정책 적용\n            \n            logger.info(f\"✅ 사용자 삭제 후속 처리 완료: {user_id}\")\n            \n        except Exception as e:\n            logger.error(f\"❌ 사용자 삭제 이벤트 처리 중 오류: {e}\")\n            raise\n    \n    async def _handle_user_login(self, event_data: Dict[str, Any], headers: Dict[str, Any]):\n        \"\"\"\n        사용자 로그인 이벤트 처리\n        \"\"\"\n        try:\n            user_id = event_data.get('user_id')\n            login_data = event_data.get('data', {})\n            \n            logger.info(f\"🔐 사용자 로그인 처리: {user_id}\")\n            \n            # 1. 로그인 통계 업데이트\n            today = datetime.now().strftime('%Y-%m-%d')\n            login_stats_key = f\"login_stats:{today}\"\n            \n            # Redis에서 일일 로그인 수 증가\n            try:\n                current_count = await redis_service.get_cache(login_stats_key) or 0\n                await redis_service.set_cache(\n                    login_stats_key, \n                    int(current_count) + 1, \n                    expire=86400  # 24시간\n                )\n            except Exception as e:\n                logger.warning(f\"⚠️ 로그인 통계 업데이트 실패: {e}\")\n            \n            # 2. 마지막 로그인 시간 저장\n            last_login_key = f\"last_login:{user_id}\"\n            await redis_service.set_cache(\n                last_login_key,\n                {\n                    \"login_time\": login_data.get('login_at'),\n                    \"login_count\": login_data.get('login_count', 1)\n                },\n                expire=2592000  # 30일\n            )\n            \n            # 3. 로그인 활동 기록\n            await self._log_user_activity(\n                user_id=user_id,\n                activity=\"user_login\",\n                details=login_data\n            )\n            \n        except Exception as e:\n            logger.error(f\"❌ 사용자 로그인 이벤트 처리 중 오류: {e}\")\n            raise\n    \n    async def _handle_user_logout(self, event_data: Dict[str, Any], headers: Dict[str, Any]):\n        \"\"\"\n        사용자 로그아웃 이벤트 처리\n        \"\"\"\n        try:\n            user_id = event_data.get('user_id')\n            \n            logger.info(f\"🔓 사용자 로그아웃 처리: {user_id}\")\n            \n            # 로그아웃 활동 기록\n            await self._log_user_activity(\n                user_id=user_id,\n                activity=\"user_logout\",\n                details=event_data.get('data', {})\n            )\n            \n        except Exception as e:\n            logger.error(f\"❌ 사용자 로그아웃 이벤트 처리 중 오류: {e}\")\n            raise\n    \n    async def _handle_unknown_event(self, event_data: Dict[str, Any]):\n        \"\"\"\n        알 수 없는 이벤트 처리\n        \"\"\"\n        try:\n            logger.warning(f\"❓ 알 수 없는 이벤트: {event_data.get('event_type')}\")\n            \n            # 미처리 이벤트를 별도 저장소에 기록 (분석용)\n            unknown_event_key = f\"unknown_events:{datetime.now().strftime('%Y-%m-%d')}\"\n            \n            # 기존 미처리 이벤트 목록 조회\n            unknown_events = await redis_service.get_cache(unknown_event_key) or []\n            \n            # 새 이벤트 추가\n            unknown_events.append({\n                \"event_data\": event_data,\n                \"timestamp\": datetime.now().isoformat()\n            })\n            \n            # 저장 (하루 보관)\n            await redis_service.set_cache(unknown_event_key, unknown_events, expire=86400)\n            \n        except Exception as e:\n            logger.error(f\"❌ 미처리 이벤트 저장 중 오류: {e}\")\n    \n    # 유틸리티 메서드들\n    \n    async def _log_user_activity(self, user_id: int, activity: str, details: Dict[str, Any]):\n        \"\"\"\n        사용자 활동 로그 기록\n        \n        실제 환경에서는 데이터베이스나 로깅 시스템에 저장합니다.\n        \"\"\"\n        try:\n            activity_log = {\n                \"user_id\": user_id,\n                \"activity\": activity,\n                \"details\": details,\n                \"timestamp\": datetime.now().isoformat()\n            }\n            \n            # Redis에 최근 활동 저장 (예시)\n            activity_key = f\"user_activities:{user_id}\"\n            recent_activities = await redis_service.get_cache(activity_key) or []\n            \n            # 최근 10개 활동만 유지\n            recent_activities.append(activity_log)\n            if len(recent_activities) > 10:\n                recent_activities = recent_activities[-10:]\n            \n            await redis_service.set_cache(activity_key, recent_activities, expire=604800)  # 7일\n            \n            logger.info(f\"📝 사용자 활동 로그 기록: {user_id} - {activity}\")\n            \n        except Exception as e:\n            logger.error(f\"❌ 사용자 활동 로그 기록 중 오류: {e}\")\n    \n    async def _send_welcome_email(self, email: str, name: str):\n        \"\"\"\n        환영 이메일 발송 (시뮬레이션)\n        \n        실제 환경에서는 이메일 서비스 API를 호출합니다.\n        \"\"\"\n        try:\n            logger.info(f\"📧 환영 이메일 발송 시뮬레이션: {email} ({name})\")\n            \n            # 실제로는 SendGrid, AWS SES 등의 이메일 서비스 사용\n            # await email_service.send_welcome_email(email, name)\n            \n            # 이메일 발송 로그를 Redis에 저장\n            email_log = {\n                \"type\": \"welcome_email\",\n                \"recipient\": email,\n                \"name\": name,\n                \"sent_at\": datetime.now().isoformat(),\n                \"status\": \"sent\"\n            }\n            \n            email_log_key = f\"email_logs:{datetime.now().strftime('%Y-%m-%d')}\"\n            email_logs = await redis_service.get_cache(email_log_key) or []\n            email_logs.append(email_log)\n            \n            await redis_service.set_cache(email_log_key, email_logs, expire=86400)\n            \n        except Exception as e:\n            logger.error(f\"❌ 환영 이메일 발송 중 오류: {e}\")\n    \n    async def _log_stats(self):\n        \"\"\"\n        처리 통계 로그 출력\n        \"\"\"\n        try:\n            uptime = datetime.now() - self.start_time\n            rate = self.processed_count / uptime.total_seconds() if uptime.total_seconds() > 0 else 0\n            \n            logger.info(\n                f\"📊 처리 통계: 처리된 메시지 {self.processed_count}개, \"\n                f\"에러 {self.error_count}개, \"\n                f\"처리 속도 {rate:.2f}개/초, \"\n                f\"실행 시간 {uptime}\"\n            )\n            \n        except Exception as e:\n            logger.error(f\"❌ 통계 로그 출력 중 오류: {e}\")\n    \n    def _signal_handler(self, signum, frame):\n        \"\"\"\n        시그널 핸들러 (Graceful Shutdown)\n        \n        Ctrl+C나 SIGTERM 시그널을 받으면 안전하게 종료합니다.\n        \"\"\"\n        logger.info(f\"🛑 종료 신호 수신 (시그널: {signum})\")\n        self.running = False\n    \n    async def _shutdown(self):\n        \"\"\"\n        컨슈머 안전 종료\n        \n        모든 리소스를 정리하고 통계를 출력합니다.\n        \"\"\"\n        try:\n            logger.info(\"🔄 컨슈머 종료 중...\")\n            \n            if self.consumer:\n                self.consumer.close()\n                logger.info(\"✅ Kafka Consumer 연결 종료\")\n            \n            # 최종 통계 출력\n            await self._log_stats()\n            \n            logger.info(\"✅ 사용자 이벤트 컨슈머 종료 완료\")\n            \n        except Exception as e:\n            logger.error(f\"❌ 컨슈머 종료 중 오류: {e}\")\n\n\n# 컨슈머 인스턴스 생성 및 실행\nasync def main():\n    \"\"\"\n    메인 실행 함수\n    \n    컨슈머를 생성하고 시작합니다.\n    \"\"\"\n    try:\n        # 컨슈머 생성\n        consumer = UserEventConsumer(group_id=\"user_event_processor\")\n        \n        # 컨슈머 시작\n        await consumer.start()\n        \n    except KeyboardInterrupt:\n        logger.info(\"⏹️ 사용자 중단\")\n    except Exception as e:\n        logger.error(f\"❌ 메인 실행 중 오류: {e}\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    \"\"\"\n    스크립트 직접 실행 시 컨슈머 시작\n    \n    사용법:\n        python consumers/user_consumer.py\n    \n    또는 백그라운드 실행:\n        python consumers/user_consumer.py &\n    \"\"\"\n    logger.info(\"🚀 사용자 이벤트 컨슈머 시작\")\n    \n    try:\n        # 이벤트 루프 실행\n        asyncio.run(main())\n    except KeyboardInterrupt:\n        logger.info(\"⏹️ 컨슈머 종료\")\n    except Exception as e:\n        logger.error(f\"❌ 실행 중 오류: {e}\")\n        sys.exit(1)"