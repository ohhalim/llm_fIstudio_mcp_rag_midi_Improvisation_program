# 해시테이블, 스택, 큐 문제

## 문제 1: 괄호 유효성 검사 (Easy)
**시간 제한**: 15분

괄호가 올바르게 열리고 닫혔는지 확인하세요.

```python
def is_valid_parentheses(s):
    """
    예시:
    Input: s = "()"
    Output: True
    
    Input: s = "()[]{}"
    Output: True
    
    Input: s = "(]"
    Output: False
    
    Input: s = "([)]"
    Output: False
    """
    pass
```

## 문제 2: 문자 빈도 카운트 (Medium)
**시간 제한**: 20분

두 문자열이 anagram인지 확인하세요. (같은 문자를 다른 순서로 배열한 것)

```python
def is_anagram(s, t):
    """
    예시:
    Input: s = "anagram", t = "nagaram"
    Output: True
    
    Input: s = "rat", t = "car"
    Output: False
    
    추가 도전: 공간복잡도 O(1)로 해결해보세요
    """
    pass
```

## 문제 3: 큐를 이용한 스택 구현 (Medium)
**시간 제한**: 25분

큐 두 개만을 사용해서 스택을 구현하세요.

```python
from collections import deque

class MyStack:
    def __init__(self):
        """
        두 개의 큐를 사용해서 스택 구현
        """
        pass
    
    def push(self, x):
        """스택에 원소 추가"""
        pass
    
    def pop(self):
        """스택에서 원소 제거하고 반환"""
        pass
    
    def top(self):
        """스택 맨 위 원소 반환 (제거하지 않음)"""
        pass
    
    def empty(self):
        """스택이 비었는지 확인"""
        pass

# 사용 예시:
# stack = MyStack()
# stack.push(1)
# stack.push(2)
# print(stack.top())    # 2
# print(stack.pop())    # 2
# print(stack.empty())  # False
```

## 문제 4: 해시맵으로 LRU 캐시 구현 (Hard)
**시간 제한**: 30분

Least Recently Used 캐시를 구현하세요. 백엔드에서 자주 사용되는 패턴입니다.

```python
class LRUCache:
    def __init__(self, capacity):
        """
        capacity: 최대 저장 가능한 아이템 수
        """
        pass
    
    def get(self, key):
        """
        키에 해당하는 값을 반환. 없으면 -1
        접근한 아이템은 가장 최근 사용됨으로 표시
        """
        pass
    
    def put(self, key, value):
        """
        키-값 쌍을 저장
        용량 초과시 가장 오래 사용되지 않은 아이템 제거
        """
        pass

# 사용 예시:
# cache = LRUCache(2)
# cache.put(1, 1)
# cache.put(2, 2)
# print(cache.get(1))    # 1
# cache.put(3, 3)        # key 2 제거됨
# print(cache.get(2))    # -1 (찾을 수 없음)
```

## 💡 백엔드 개발자를 위한 학습 포인트
- **해시맵**: 데이터베이스 인덱싱, 캐싱 시스템
- **스택**: 함수 호출 스택, 실행 취소 기능
- **큐**: 메시지 큐, 작업 스케줄링
- **LRU 캐시**: Redis, 메모리 관리 시스템

## 🔧 실제 백엔드 활용 사례
- **API 응답 캐싱**: LRU로 자주 요청되는 데이터 캐싱
- **세션 관리**: 해시맵으로 사용자 세션 저장
- **큐 시스템**: 비동기 작업 처리 (Celery, RabbitMQ)
- **로그 처리**: 스택으로 에러 추적, 큐로 로그 버퍼링