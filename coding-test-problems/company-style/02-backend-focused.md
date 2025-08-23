# 백엔드 특화 문제

## 문제 1: API 레이트 리미팅 (Medium)
**시간 제한**: 30분

토큰 버킷 알고리즘을 구현하여 API 요청을 제한하세요.

```python
import time

class RateLimiter:
    def __init__(self, capacity, refill_rate):
        """
        capacity: 버킷 용량 (최대 토큰 수)
        refill_rate: 초당 토큰 충전량
        """
        pass
    
    def is_allowed(self, tokens_needed=1):
        """
        요청이 허용되는지 확인
        
        예시:
        limiter = RateLimiter(capacity=10, refill_rate=2)
        
        # 초기에는 10개 토큰 보유
        limiter.is_allowed(5)  # True, 5개 토큰 사용, 5개 남음
        limiter.is_allowed(6)  # False, 토큰 부족
        
        # 1초 후 2개 토큰 충전 (총 7개)
        time.sleep(1)
        limiter.is_allowed(6)  # True, 1개 남음
        """
        pass

# 실제 사용 시나리오 테스트
def test_rate_limiter():
    # 분당 60회 요청 제한 (초당 1회)
    limiter = RateLimiter(capacity=60, refill_rate=1)
    
    # 연속 60회 요청
    for i in range(60):
        assert limiter.is_allowed() == True
    
    # 61번째 요청은 거부
    assert limiter.is_allowed() == False
    
    print("Rate limiter test passed!")
```

## 문제 2: 데이터베이스 커넥션 풀 (Medium)
**시간 제한**: 35분

데이터베이스 커넥션 풀을 구현하세요.

```python
import threading
import queue
import time

class Connection:
    def __init__(self, conn_id):
        self.conn_id = conn_id
        self.in_use = False
        self.created_at = time.time()
    
    def execute_query(self, query):
        # 가상의 쿼리 실행
        time.sleep(0.1)  # 쿼리 실행 시간 시뮬레이션
        return f"Result for {query} from connection {self.conn_id}"

class ConnectionPool:
    def __init__(self, min_connections=5, max_connections=20, max_idle_time=300):
        """
        min_connections: 최소 커넥션 수
        max_connections: 최대 커넥션 수  
        max_idle_time: 최대 유휴 시간 (초)
        """
        pass
    
    def get_connection(self, timeout=10):
        """
        커넥션을 가져오기. timeout 초 내에 없으면 None 반환
        """
        pass
    
    def return_connection(self, connection):
        """
        사용 완료된 커넥션을 풀에 반환
        """
        pass
    
    def cleanup_idle_connections(self):
        """
        유휴 시간이 초과된 커넥션들을 정리
        """
        pass
    
    def get_stats(self):
        """
        풀의 현재 상태 반환
        return: {"total": int, "active": int, "idle": int}
        """
        pass

# 사용 예시
def database_service_example():
    pool = ConnectionPool(min_connections=2, max_connections=10)
    
    # 동시 요청 처리
    def worker():
        conn = pool.get_connection()
        if conn:
            result = conn.execute_query("SELECT * FROM users")
            pool.return_connection(conn)
            return result
        return "No connection available"
    
    # 멀티스레딩 테스트
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker) for _ in range(10)]
        results = [future.result() for future in futures]
    
    print("Connection pool test completed")
```

## 문제 3: 로그 수집 시스템 (Hard)
**시간 제한**: 45분

대용량 로그를 실시간으로 수집하고 분석하는 시스템을 구현하세요.

```python
import heapq
from collections import defaultdict, deque
import threading
import time

class LogProcessor:
    def __init__(self, window_size=60):
        """
        window_size: 분석 시간 윈도우 (초)
        """
        self.window_size = window_size
        self.logs = deque()
        self.error_count = defaultdict(int)
        self.request_count = 0
        self.response_times = []
        self.lock = threading.Lock()
    
    def add_log(self, log_entry):
        """
        로그 엔트리 추가
        
        log_entry = {
            "timestamp": 1640995200.0,
            "level": "ERROR",
            "message": "Database connection failed",
            "service": "user-service",
            "response_time": 250  # milliseconds
        }
        """
        pass
    
    def get_error_rate(self):
        """
        최근 window_size 초 동안의 에러율 반환 (0.0 ~ 1.0)
        """
        pass
    
    def get_average_response_time(self):
        """
        최근 window_size 초 동안의 평균 응답 시간 반환 (밀리초)
        """
        pass
    
    def get_top_errors(self, limit=5):
        """
        최근 window_size 초 동안 가장 많이 발생한 에러 Top N
        return: [(error_message, count), ...]
        """
        pass
    
    def cleanup_old_logs(self):
        """
        윈도우 시간을 벗어난 오래된 로그 제거
        """
        pass

class AlertManager:
    def __init__(self, log_processor):
        self.log_processor = log_processor
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5% 이상
            "avg_response_time": 1000,  # 1초 이상
        }
        self.alerts = []
    
    def check_alerts(self):
        """
        알림 조건을 체크하고 필요시 알림 생성
        """
        pass
    
    def send_alert(self, alert_type, message, severity="WARN"):
        """
        알림 발송 (실제로는 Slack, Email 등으로 발송)
        """
        alert = {
            "timestamp": time.time(),
            "type": alert_type,
            "message": message,
            "severity": severity
        }
        self.alerts.append(alert)
        print(f"🚨 ALERT [{severity}]: {message}")

# 사용 예시 및 테스트
def test_log_processing():
    processor = LogProcessor(window_size=10)  # 10초 윈도우
    alert_manager = AlertManager(processor)
    
    # 샘플 로그 데이터 생성
    import random
    current_time = time.time()
    
    for i in range(100):
        log_entry = {
            "timestamp": current_time - random.uniform(0, 15),
            "level": random.choice(["INFO", "WARN", "ERROR"]),
            "message": f"Sample log message {i}",
            "service": random.choice(["user-service", "order-service", "payment-service"]),
            "response_time": random.randint(50, 2000)
        }
        processor.add_log(log_entry)
    
    # 분석 결과 출력
    print(f"Error rate: {processor.get_error_rate():.2%}")
    print(f"Average response time: {processor.get_average_response_time():.0f}ms")
    print("Top errors:", processor.get_top_errors(3))
    
    # 알림 체크
    alert_manager.check_alerts()
```

## 문제 4: 분산 시스템 일관성 (Hard)
**시간 제한**: 50분

분산 캐시 시스템에서 데이터 일관성을 보장하는 메커니즘을 구현하세요.

```python
import hashlib
import threading
from typing import Dict, List, Optional

class ConsistentHash:
    def __init__(self, nodes: List[str], replicas: int = 3):
        """
        일관성 해싱을 구현한 분산 캐시
        nodes: 노드 리스트 (서버 목록)
        replicas: 가상 노드 수 (부하 분산용)
        """
        pass
    
    def _hash(self, key: str) -> int:
        """문자열을 해시값으로 변환"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str):
        """새로운 노드 추가 (스케일 아웃)"""
        pass
    
    def remove_node(self, node: str):
        """노드 제거 (장애 상황)"""
        pass
    
    def get_node(self, key: str) -> str:
        """키에 대한 담당 노드 반환"""
        pass

class DistributedCache:
    def __init__(self, nodes: List[str]):
        self.consistent_hash = ConsistentHash(nodes)
        self.local_cache = {}  # 로컬 캐시 시뮬레이션
        self.version_vector = {}  # 벡터 클락으로 버전 관리
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[str]:
        """
        키에 해당하는 값을 가져옴
        캐시 미스시 데이터베이스에서 조회 후 캐시에 저장
        """
        pass
    
    def put(self, key: str, value: str, ttl: int = 3600):
        """
        키-값 쌍을 저장하고 다른 노드들에게 전파
        ttl: Time To Live (초)
        """
        pass
    
    def invalidate(self, key: str):
        """
        키를 무효화하고 모든 노드에 전파
        """
        pass
    
    def replicate(self, key: str, value: str, node: str):
        """
        다른 노드로 데이터 복제
        """
        pass
    
    def handle_node_failure(self, failed_node: str):
        """
        노드 장애 처리 및 데이터 재분배
        """
        pass

# 실제 사용 시나리오
def test_distributed_cache():
    # 3개 노드로 클러스터 구성
    cache = DistributedCache(["node1", "node2", "node3"])
    
    # 데이터 저장
    cache.put("user:1001", '{"name": "Alice", "age": 25}')
    cache.put("user:1002", '{"name": "Bob", "age": 30}')
    
    # 데이터 조회
    user1 = cache.get("user:1001")
    print(f"Retrieved: {user1}")
    
    # 노드 장애 시뮬레이션
    cache.handle_node_failure("node2")
    
    # 장애 후에도 데이터 접근 가능한지 확인
    user2 = cache.get("user:1002")
    print(f"After node failure: {user2}")
```

## 💡 백엔드 시스템 설계 핵심 개념

### 1. 확장성 (Scalability)
- **수평 확장**: 서버 추가로 처리량 증가
- **수직 확장**: 서버 성능 향상으로 처리량 증가
- **일관성 해싱**: 노드 추가/제거 시 데이터 재분배 최소화

### 2. 가용성 (Availability)
- **부하 분산**: 트래픽을 여러 서버에 분산
- **장애 복구**: 자동 장애 감지 및 복구
- **데이터 복제**: 중복 저장으로 데이터 손실 방지

### 3. 일관성 (Consistency)
- **강한 일관성**: 모든 노드에서 동일한 데이터
- **최종 일관성**: 시간이 지나면 일관성 보장
- **인과적 일관성**: 인과관계가 있는 연산 순서 보장

## 🔧 실제 시스템에서의 활용

```python
# Redis 클러스터 구성
class RedisClusterClient:
    def __init__(self, nodes):
        self.consistent_hash = ConsistentHash(nodes)
    
    def set(self, key, value):
        node = self.consistent_hash.get_node(key)
        # 실제로는 Redis 노드에 저장
        return f"SET {key}={value} on {node}"

# 마이크로서비스 간 통신
class ServiceMesh:
    def __init__(self):
        self.rate_limiter = RateLimiter(100, 10)  # 초당 10개 토큰
    
    def call_service(self, service_name, request):
        if not self.rate_limiter.is_allowed():
            raise Exception("Rate limit exceeded")
        # 서비스 호출
        return f"Called {service_name} with {request}"
```

## ⚡ 성능 최적화 팁

### 메모리 관리
```python
# 메모리 효율적인 데이터 구조 사용
from collections import deque
import sys

# 큐 크기 제한
log_buffer = deque(maxlen=10000)

# 약한 참조로 메모리 누수 방지
import weakref
cache = weakref.WeakValueDictionary()
```

### 동시성 처리
```python
# 스레드 안전한 자료구조
import queue
import threading

# 스레드 풀로 리소스 관리
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=10)
```

## 🎯 면접 대비 포인트
- **CAP 이론**: 일관성, 가용성, 분할 내성 중 2개만 선택 가능
- **ACID vs BASE**: 강한 일관성 vs 최종 일관성
- **로드 밸런싱 알고리즘**: Round Robin, Weighted, Least Connections
- **캐싱 전략**: Cache-aside, Write-through, Write-back

이 문제들을 해결할 수 있다면 시니어 백엔드 개발자 수준의 역량을 갖췄다고 볼 수 있습니다!