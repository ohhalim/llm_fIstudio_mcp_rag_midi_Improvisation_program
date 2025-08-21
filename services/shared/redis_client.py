import redis.asyncio as redis
import json
from typing import Any, Optional
from .config import RedisSettings

class RedisClient:
    def __init__(self, settings: RedisSettings):
        self.settings = settings
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Redis 연결"""
        self.redis_client = redis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Redis 연결 해제"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """키-값 저장"""
        if not self.redis_client:
            await self.connect()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return await self.redis_client.set(key, value, ex=ex)
    
    async def get(self, key: str) -> Optional[Any]:
        """키로 값 조회"""
        if not self.redis_client:
            await self.connect()
        
        value = await self.redis_client.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def delete(self, key: str) -> bool:
        """키 삭제"""
        if not self.redis_client:
            await self.connect()
        
        result = await self.redis_client.delete(key)
        return result > 0
    
    async def exists(self, key: str) -> bool:
        """키 존재 확인"""
        if not self.redis_client:
            await self.connect()
        
        return await self.redis_client.exists(key) > 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """키 만료 시간 설정"""
        if not self.redis_client:
            await self.connect()
        
        return await self.redis_client.expire(key, seconds)
    
    async def publish(self, channel: str, message: Any):
        """메시지 발행 (pub/sub)"""
        if not self.redis_client:
            await self.connect()
        
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        
        return await self.redis_client.publish(channel, message)
    
    async def subscribe(self, channel: str):
        """채널 구독 (pub/sub)"""
        if not self.redis_client:
            await self.connect()
        
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

# 글로벌 Redis 클라이언트
redis_client: Optional[RedisClient] = None

def init_redis(settings: RedisSettings) -> RedisClient:
    global redis_client
    redis_client = RedisClient(settings)
    return redis_client

async def get_redis() -> RedisClient:
    """FastAPI 의존성으로 사용할 Redis 클라이언트"""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    return redis_client