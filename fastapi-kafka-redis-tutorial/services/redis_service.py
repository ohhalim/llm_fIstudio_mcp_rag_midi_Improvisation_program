"""
services/redis_service.py - Redis 캐시 서비스

이 파일에서 배울 수 있는 개념들:
1. Redis 연결 및 관리
2. 캐시 패턴 (Cache-Aside, Write-Through 등)
3. 데이터 직렬화/역직렬화 (JSON)
4. 에러 핸들링과 로깅
5. 싱글톤 패턴
6. 비동기 프로그래밍 (async/await)
"""

import redis
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from config import settings
from models import User, Item


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisService:
    """
    Redis 캐시 서비스 클래스
    
    싱글톤 패턴을 사용하여 애플리케이션 전체에서 하나의 인스턴스만 사용합니다.
    캐시의 일관성을 유지하고 연결 리소스를 효율적으로 관리할 수 있습니다.
    """
    
    _instance = None  # 싱글톤 인스턴스 저장
    
    def __new__(cls):
        """
        싱글톤 패턴 구현
        
        __new__ 메서드를 오버라이드하여 인스턴스를 하나만 생성하도록 합니다.
        """
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Redis 클라이언트 초기화
        """
        if not hasattr(self, 'initialized'):
            try:
                # Redis 연결 설정
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    db=settings.redis_db,
                    max_connections=settings.redis_max_connections,
                    decode_responses=True,  # 자동으로 bytes를 str로 디코딩
                    socket_keepalive=True,  # TCP keepalive 활성화
                    socket_keepalive_options={},
                    retry_on_timeout=True  # 타임아웃 시 재시도
                )
                
                # 연결 테스트
                self.redis_client.ping()
                logger.info("✅ Redis 연결 성공")
                self.initialized = True
                
            except redis.RedisError as e:
                logger.error(f"❌ Redis 연결 실패: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ Redis 초기화 중 예상치 못한 오류: {e}")
                raise
    
    # 기본 캐시 operations
    async def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        캐시에 데이터 저장
        
        Args:
            key (str): 캐시 키
            value (Any): 저장할 값 (dict, list, str 등)
            expire (int): 만료 시간(초), 기본값 1시간
            
        Returns:
            bool: 저장 성공 여부
            
        캐시 패턴: Cache-Aside (애플리케이션이 캐시를 직접 관리)
        """
        try:
            # 객체를 JSON 문자열로 직렬화
            serialized_value = json.dumps(
                value, 
                default=self._json_serializer,
                ensure_ascii=False
            )
            
            # Redis에 저장 (setex: set with expiration)
            result = self.redis_client.setex(key, expire, serialized_value)
            
            logger.info(f"✅ 캐시 저장 성공: {key} (TTL: {expire}초)")
            return result
            
        except redis.RedisError as e:
            logger.error(f"❌ Redis 저장 오류 ({key}): {e}")
            return False
        except (TypeError, ValueError) as e:
            logger.error(f"❌ 직렬화 오류 ({key}): {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 캐시 저장 중 예상치 못한 오류 ({key}): {e}")
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """
        캐시에서 데이터 조회
        
        Args:
            key (str): 캐시 키
            
        Returns:
            Optional[Any]: 캐시된 데이터 또는 None
        """
        try:
            # Redis에서 데이터 가져오기
            cached_data = self.redis_client.get(key)
            
            if cached_data is None:
                logger.info(f"🔍 캐시 미스: {key}")
                return None
            
            # JSON 문자열을 객체로 역직렬화
            deserialized_data = json.loads(cached_data)
            logger.info(f"✅ 캐시 히트: {key}")
            
            return deserialized_data
            
        except redis.RedisError as e:
            logger.error(f"❌ Redis 조회 오류 ({key}): {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ 역직렬화 오류 ({key}): {e}")
            # 손상된 캐시 데이터 삭제
            await self.delete_cache(key)
            return None
        except Exception as e:
            logger.error(f"❌ 캐시 조회 중 예상치 못한 오류 ({key}): {e}")
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """
        캐시 삭제
        
        Args:
            key (str): 삭제할 캐시 키
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            result = self.redis_client.delete(key)
            if result:
                logger.info(f"✅ 캐시 삭제 성공: {key}")
            else:
                logger.info(f"🔍 삭제할 캐시 없음: {key}")
            return bool(result)
            
        except redis.RedisError as e:
            logger.error(f"❌ Redis 삭제 오류 ({key}): {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 캐시 삭제 중 예상치 못한 오류 ({key}): {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        캐시 키 존재 여부 확인
        """
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            logger.error(f"❌ Redis exists 오류 ({key}): {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """
        캐시 키의 남은 TTL(Time To Live) 조회
        
        Returns:
            int: 남은 시간(초), -1이면 만료시간 없음, -2면 키가 없음
        """
        try:
            return self.redis_client.ttl(key)
        except redis.RedisError as e:
            logger.error(f"❌ Redis TTL 조회 오류 ({key}): {e}")
            return -2
    
    # 패턴별 캐시 operations
    async def set_user_cache(self, user_id: int, user_data: Dict[str, Any], expire: int = 3600) -> bool:
        """
        사용자 캐시 저장 (특화된 메서드)
        
        네이밍 컨벤션을 일관성 있게 유지하기 위한 특화 메서드
        """
        cache_key = f"user:{user_id}"
        return await self.set_cache(cache_key, user_data, expire)
    
    async def get_user_cache(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        사용자 캐시 조회
        """
        cache_key = f"user:{user_id}"
        return await self.get_cache(cache_key)
    
    async def delete_user_cache(self, user_id: int) -> bool:
        """
        사용자 캐시 삭제
        """
        cache_key = f"user:{user_id}"
        return await self.delete_cache(cache_key)
    
    async def set_item_cache(self, item_id: int, item_data: Dict[str, Any], expire: int = 1800) -> bool:
        """
        아이템 캐시 저장 (30분 TTL)
        """
        cache_key = f"item:{item_id}"
        return await self.set_cache(cache_key, item_data, expire)
    
    async def get_item_cache(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        아이템 캐시 조회
        """
        cache_key = f"item:{item_id}"
        return await self.get_cache(cache_key)
    
    # 고급 캐시 operations
    async def get_or_set(self, key: str, fetch_func, expire: int = 3600) -> Any:
        """
        캐시가 있으면 반환, 없으면 함수 실행 후 캐시에 저장
        
        Cache-Aside 패턴의 구현체
        
        Args:
            key (str): 캐시 키
            fetch_func: 캐시 미스 시 실행할 함수
            expire (int): 캐시 만료 시간
            
        Returns:
            Any: 캐시된 데이터 또는 함수 실행 결과
        """
        # 먼저 캐시 확인
        cached_data = await self.get_cache(key)
        if cached_data is not None:
            return cached_data
        
        # 캐시 미스 - 실제 데이터 조회
        try:
            fresh_data = await fetch_func() if callable(fetch_func) else fetch_func
            if fresh_data is not None:
                # 새 데이터를 캐시에 저장
                await self.set_cache(key, fresh_data, expire)
            return fresh_data
        except Exception as e:
            logger.error(f"❌ get_or_set 함수 실행 오류 ({key}): {e}")
            return None
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        패턴에 맞는 모든 캐시 키 삭제
        
        예: "user:*" 패턴으로 모든 사용자 캐시 삭제
        
        Args:
            pattern (str): Redis 패턴 (와일드카드 * 사용 가능)
            
        Returns:
            int: 삭제된 키의 개수
        """
        try:
            # 패턴에 맞는 키들 찾기
            keys = self.redis_client.keys(pattern)
            
            if not keys:
                logger.info(f"🔍 삭제할 키 없음: {pattern}")
                return 0
            
            # 키들 삭제
            deleted_count = self.redis_client.delete(*keys)
            logger.info(f"✅ 패턴 캐시 삭제: {pattern} ({deleted_count}개)")
            
            return deleted_count
            
        except redis.RedisError as e:
            logger.error(f"❌ 패턴 캐시 삭제 오류 ({pattern}): {e}")
            return 0
    
    # 통계 및 모니터링
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Redis 캐시 통계 정보 조회
        """
        try:
            info = self.redis_client.info()
            
            stats = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
            # 캐시 적중률 계산
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            total_requests = hits + misses
            
            if total_requests > 0:
                hit_rate = (hits / total_requests) * 100
                stats["hit_rate_percentage"] = round(hit_rate, 2)
            else:
                stats["hit_rate_percentage"] = 0.0
            
            return stats
            
        except redis.RedisError as e:
            logger.error(f"❌ Redis 통계 조회 오류: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, str]:
        """
        Redis 연결 상태 확인
        
        헬스체크 엔드포인트에서 사용
        """
        try:
            # ping 명령으로 연결 상태 확인
            response = self.redis_client.ping()
            if response:
                return {
                    "status": "healthy",
                    "message": "Redis 연결 정상",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy", 
                    "message": "Redis ping 실패",
                    "timestamp": datetime.now().isoformat()
                }
        except redis.RedisError as e:
            return {
                "status": "unhealthy",
                "message": f"Redis 오류: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    # 유틸리티 메서드
    def _json_serializer(self, obj):
        """
        JSON 직렬화를 위한 커스텀 시리얼라이저
        
        datetime 객체 등을 JSON으로 변환할 때 사용
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):  # Pydantic 모델
            return obj.dict()
        elif hasattr(obj, '__dict__'):  # 일반 객체
            return obj.__dict__
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def close_connection(self):
        """
        Redis 연결 종료
        
        애플리케이션 종료 시 호출
        """
        try:
            if hasattr(self, 'redis_client'):
                self.redis_client.close()
                logger.info("✅ Redis 연결 종료")
        except Exception as e:
            logger.error(f"❌ Redis 연결 종료 중 오류: {e}")


# 싱글톤 인스턴스 생성
redis_service = RedisService()


# 편의 함수들 (모듈 레벨에서 직접 사용 가능)
async def cache_user(user_id: int, user_data: Dict[str, Any], expire: int = 3600) -> bool:
    """사용자 캐시 저장 편의 함수"""
    return await redis_service.set_user_cache(user_id, user_data, expire)


async def get_cached_user(user_id: int) -> Optional[Dict[str, Any]]:
    """사용자 캐시 조회 편의 함수"""
    return await redis_service.get_user_cache(user_id)


async def invalidate_user_cache(user_id: int) -> bool:
    """사용자 캐시 무효화 편의 함수"""
    return await redis_service.delete_user_cache(user_id)


if __name__ == "__main__":
    """
    Redis 서비스 테스트 코드
    """
    import asyncio
    
    async def test_redis_service():
        print("Redis 서비스 테스트 시작...")
        
        # 기본 캐시 operations 테스트
        test_key = "test:key"
        test_data = {"name": "테스트", "value": 123, "timestamp": datetime.now()}
        
        # 저장 테스트
        success = await redis_service.set_cache(test_key, test_data, 60)
        print(f"캐시 저장: {success}")
        
        # 조회 테스트
        cached = await redis_service.get_cache(test_key)
        print(f"캐시 조회: {cached}")
        
        # TTL 확인
        ttl = await redis_service.get_ttl(test_key)
        print(f"TTL: {ttl}초")
        
        # 삭제 테스트
        deleted = await redis_service.delete_cache(test_key)
        print(f"캐시 삭제: {deleted}")
        
        # 통계 조회
        stats = await redis_service.get_cache_stats()
        print(f"Redis 통계: {stats}")
        
        # 헬스체크
        health = await redis_service.health_check()
        print(f"헬스체크: {health}")
    
    # 비동기 테스트 실행
    asyncio.run(test_redis_service())