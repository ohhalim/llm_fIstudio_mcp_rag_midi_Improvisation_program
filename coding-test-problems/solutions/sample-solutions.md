# 샘플 솔루션

이 파일에는 몇 가지 대표 문제들의 해답과 설명이 포함되어 있습니다.

## 두 수의 합 (Two Sum) 해답

```python
def two_sum(nums, target):
    """
    해시맵을 사용한 O(n) 솔루션
    """
    num_to_index = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_to_index:
            return [num_to_index[complement], i]
        num_to_index[num] = i
    
    return []

# 시간복잡도: O(n)
# 공간복잡도: O(n)
```

## 괄호 유효성 검사 해답

```python
def is_valid_parentheses(s):
    """
    스택을 사용한 괄호 매칭
    """
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            stack.append(char)
    
    return not stack

# 시간복잡도: O(n)
# 공간복잡도: O(n)
```

## 이진 탐색 해답

```python
def binary_search(nums, target):
    """
    표준 이진 탐색 구현
    """
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# 시간복잡도: O(log n)
# 공간복잡도: O(1)
```

## 섬의 개수 해답

```python
def num_islands(grid):
    """
    DFS를 사용한 연결된 컴포넌트 찾기
    """
    if not grid:
        return 0
    
    def dfs(i, j):
        if (i < 0 or i >= len(grid) or 
            j < 0 or j >= len(grid[0]) or 
            grid[i][j] != '1'):
            return
        
        grid[i][j] = '0'  # 방문 표시
        
        # 4방향 탐색
        dfs(i+1, j)
        dfs(i-1, j)
        dfs(i, j+1)
        dfs(i, j-1)
    
    islands = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1':
                islands += 1
                dfs(i, j)
    
    return islands

# 시간복잡도: O(m × n)
# 공간복잡도: O(m × n) - 재귀 스택
```

## LRU 캐시 해답

```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []  # 사용 순서 추적
    
    def get(self, key):
        if key in self.cache:
            # 최근 사용으로 이동
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1
    
    def put(self, key, value):
        if key in self.cache:
            # 기존 키 업데이트
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # 용량 초과시 가장 오래된 것 제거
            oldest = self.order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.order.append(key)

# 더 효율적인 해답 (doubly linked list + hash map)
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCacheOptimal:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        
        # 더미 head, tail 노드
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_head(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            # 노드를 head로 이동 (최근 사용)
            self._remove_node(node)
            self._add_to_head(node)
            return node.value
        return -1
    
    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove_node(node)
            self._add_to_head(node)
        else:
            new_node = Node(key, value)
            if len(self.cache) >= self.capacity:
                # tail의 이전 노드 제거
                last = self.tail.prev
                self._remove_node(last)
                del self.cache[last.key]
            
            self.cache[key] = new_node
            self._add_to_head(new_node)

# 시간복잡도: O(1) for both get and put
# 공간복잡도: O(capacity)
```

## 피보나치 수열 해답

```python
# 방법 1: 메모이제이션 (Top-down DP)
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]

# 방법 2: 바텀업 DP
def fibonacci_dp(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

# 방법 3: 공간 최적화
def fibonacci_optimal(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    
    return b

# 시간복잡도: O(n)
# 공간복잡도: O(1) for optimal version
```

## Rate Limiter 해답

```python
import time

class TokenBucketRateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def _refill(self):
        now = time.time()
        tokens_to_add = (now - self.last_refill) * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def is_allowed(self, tokens_needed=1):
        self._refill()
        
        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False

# 더 정교한 구현 (멀티스레딩 고려)
import threading

class ThreadSafeRateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def is_allowed(self, tokens_needed=1):
        with self.lock:
            now = time.time()
            tokens_to_add = (now - self.last_refill) * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False
```

## 💡 문제 해결 접근법

### 1. 문제 분석
- 입출력 예시 분석
- 제약 조건 확인
- 시간/공간 복잡도 요구사항 파악

### 2. 알고리즘 선택
- 브루트 포스로 시작
- 최적화 방법 탐색
- 적절한 자료구조 선택

### 3. 구현 전략
- 엣지 케이스 처리
- 변수명 명확히
- 주석으로 로직 설명

### 4. 테스트 및 검증
- 예시 입력으로 테스트
- 경계 조건 확인
- 시간 복잡도 검증

## 🎯 실전 팁
- **코드 가독성**: 변수명과 함수명을 명확하게
- **에러 처리**: null, empty 입력에 대한 처리
- **최적화**: 불필요한 계산 제거, 캐싱 활용
- **검증**: 시간 복잡도가 요구사항을 만족하는지 확인