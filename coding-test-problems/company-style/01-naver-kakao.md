# 네이버・카카오 스타일 문제

## 문제 1: 카카오 - 압축 (2018 카카오 블라인드)
**시간 제한**: 40분

LZW 압축 알고리즘을 구현하세요.

```python
def solution(msg):
    """
    주어진 문자열을 LZW 압축하여 출력 배열을 반환
    
    예시:
    Input: msg = "KAKAO"
    Output: [11, 1, 27, 15]
    
    Input: msg = "TOBEORNOTTOBEORTOBEORNOT"
    Output: [20, 15, 2, 5, 15, 18, 14, 15, 20, 27, 29, 31, 36, 30, 32, 34]
    
    규칙:
    1. 사전에 A=1, B=2, ..., Z=26 초기화
    2. 가장 긴 문자열 w를 찾아서 색인 출력
    3. w+c를 사전에 등록 (c는 다음 글자)
    4. 입력에서 w를 제거
    5. 처리할 글자가 남아있다면 2단계부터 반복
    """
    pass
```

## 문제 2: 네이버 - 서버 부하 분산
**시간 제한**: 35분

여러 서버에 작업을 균등하게 분배하여 최대 부하를 최소화하세요.

```python
def distribute_load(servers, tasks):
    """
    각 서버의 처리 능력과 작업들이 주어졌을 때,
    최대 부하를 최소화하는 작업 분배 방법 찾기
    
    예시:
    Input: servers = [3, 2, 4], tasks = [1, 2, 3, 4, 5]
    Output: 4 (최대 부하)
    
    서버별 할당:
    Server 0 (capacity=3): tasks [5] → load = 5/3 = 1.67
    Server 1 (capacity=2): tasks [4] → load = 4/2 = 2.0  
    Server 2 (capacity=4): tasks [1,2,3] → load = 6/4 = 1.5
    최대 부하 = 2.0
    
    return: 최대 부하 (소수점 둘째자리까지)
    """
    pass
```

## 문제 3: 카카오 - 캐시 (2018 카카오 블라인드)
**시간 제한**: 30분

LRU 캐시 교체 알고리즘을 구현하세요.

```python
def solution(cacheSize, cities):
    """
    캐시 교체 알고리즘 구현하여 총 실행시간 계산
    
    예시:
    Input: cacheSize = 3, cities = ["Jeju", "Pangyo", "Seoul", "NewYork", "LA", "Jeju", "Pangyo", "Seoul", "NewYork", "LA"]
    Output: 50
    
    규칙:
    - 캐시 hit: 실행시간 1
    - 캐시 miss: 실행시간 5
    - 도시 이름은 대소문자 구분 없음
    - cacheSize가 0이면 모든 경우가 miss
    
    과정:
    Jeju(miss): cache=["Jeju"], time=5
    Pangyo(miss): cache=["Jeju","Pangyo"], time=10
    Seoul(miss): cache=["Jeju","Pangyo","Seoul"], time=15
    NewYork(miss): cache=["Pangyo","Seoul","NewYork"], time=20 (Jeju 제거)
    ...
    """
    pass
```

## 문제 4: 네이버 - 추천 시스템
**시간 제한**: 45분

사용자 행동 로그를 분석하여 상품 추천 점수를 계산하세요.

```python
def recommend_products(user_logs, target_user):
    """
    사용자 행동 로그를 분석하여 target_user에게 추천할 상품 리스트 반환
    
    예시:
    Input: user_logs = [
        ["user1", "view", "product1", 10],
        ["user1", "cart", "product1", 20],
        ["user1", "purchase", "product1", 50],
        ["user2", "view", "product2", 10],
        ["user1", "view", "product2", 10],
        ["user2", "purchase", "product2", 50]
    ], target_user = "user1"
    Output: ["product2"]
    
    규칙:
    - 각 행동의 점수: view=10, cart=20, purchase=50
    - 이미 구매한 상품은 추천하지 않음
    - 같은 상품에 대해 다른 사용자들의 구매율이 높은 순서로 정렬
    - 구매율 = (구매한 사용자 수) / (본 사용자 수)
    
    형식: [user_id, action, product_id, score]
    """
    pass
```

## 문제 5: 카카오 - 순위 검색 (2021 카카오 블라인드)
**시간 제한**: 50분

개발자 지원서를 효율적으로 검색하는 시스템을 구현하세요.

```python
def solution(info, query):
    """
    지원자 정보와 검색 쿼리가 주어졌을 때, 조건을 만족하는 지원자 수 반환
    
    예시:
    Input: info = ["java backend junior pizza 150",
                  "python frontend senior chicken 210",
                  "python frontend senior chicken 150",
                  "cpp backend senior pizza 260",
                  "java backend junior chicken 80",
                  "python backend senior chicken 50"]
           query = ["java and backend and junior and pizza 100",
                   "python and frontend and senior and chicken 200",
                   "cpp and - and senior and pizza 250",
                   "- and backend and senior and - 150",
                   "- and - and - and chicken 100",
                   "- and - and - and - 150"]
    Output: [1, 1, 1, 1, 2, 4]
    
    규칙:
    - 언어: cpp, java, python
    - 직군: backend, frontend  
    - 경력: junior, senior
    - 소울푸드: chicken, pizza
    - '-'는 모든 조건 허용
    - 점수는 쿼리 점수 이상인 지원자만 카운트
    
    효율성을 위해 이진 탐색 활용 필요!
    """
    pass
```

## 💡 한국 IT 기업 출제 경향

### 네이버 특징
- **시스템 설계** 관련 문제 선호
- **효율성** 중시 (시간복잡도 최적화)
- **실제 서비스** 상황을 문제로 만듦
- **대용량 데이터** 처리 능력 평가

### 카카오 특징  
- **구현력** 중시 (복잡한 로직 구현)
- **문자열 처리** 문제 자주 출제
- **시뮬레이션** 문제 선호
- **단계별 해결** 과정 중요

## 🔧 백엔드 관련 핵심 개념

```python
# 캐싱 전략
class LRUCache:
    # 실제 Redis, Memcached에서 사용하는 알고리즘
    pass

# 로드 밸런싱
def weighted_round_robin(servers, weights):
    # 실제 nginx, HAProxy에서 사용하는 방식
    pass

# 검색 최적화
def build_inverted_index(documents):
    # 실제 Elasticsearch에서 사용하는 개념
    pass
```

## ⚡ 실전 팁

### 효율성 테스트 대비
- **시간 복잡도**: O(N log N) 이하로 최적화
- **공간 복잡도**: 메모리 제한 고려
- **자료구조 선택**: dict, set, deque 적절히 활용

### 구현 실수 방지
- **엣지 케이스**: 빈 입력, 단일 원소
- **인덱스 범위**: 배열 경계 체크
- **대소문자**: 문제에서 구분 여부 확인
- **정렬 안정성**: 동점 처리 방식

## 🎯 학습 순서
1. **기본 알고리즘** 숙달 후 응용 문제 도전
2. **시뮬레이션** 문제로 구현력 향상
3. **효율성** 문제로 최적화 능력 개발
4. **실제 기출문제** 반복 연습

이 수준의 문제들을 해결할 수 있다면 대부분의 한국 IT 기업 코딩테스트를 통과할 수 있습니다!