# 동적 프로그래밍 (Dynamic Programming)

## 문제 1: 피보나치 수열 (Easy)
**시간 제한**: 15분

피보나치 수열의 n번째 수를 구하세요. 효율적인 방법으로 해결하세요.

```python
def fibonacci(n):
    """
    예시:
    Input: n = 2
    Output: 1
    
    Input: n = 3
    Output: 2
    
    Input: n = 4
    Output: 3
    
    F(0) = 0, F(1) = 1
    F(n) = F(n-1) + F(n-2) for n > 1
    
    방법 1: 재귀 (비효율적) - O(2^n)
    방법 2: 메모이제이션 - O(n)
    방법 3: 바텀업 DP - O(n), 공간 O(1)
    """
    pass
```

## 문제 2: 계단 오르기 (Easy)
**시간 제한**: 20분

계단을 오르는데, 한 번에 1개 또는 2개의 계단을 오를 수 있습니다. n개의 계단을 오르는 방법의 수를 구하세요.

```python
def climb_stairs(n):
    """
    예시:
    Input: n = 2
    Output: 2 (1+1, 2)
    
    Input: n = 3
    Output: 3 (1+1+1, 1+2, 2+1)
    
    Input: n = 4
    Output: 5 (1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2)
    
    패턴을 찾아보세요!
    """
    pass
```

## 문제 3: 최소 비용 경로 (Medium)
**시간 제한**: 25분

2D 그리드에서 왼쪽 상단에서 오른쪽 하단까지 가는 최소 비용 경로를 찾으세요.

```python
def min_path_sum(grid):
    """
    예시:
    Input: grid = [[1,3,1],
                  [1,5,1],
                  [4,2,1]]
    Output: 7 (경로: 1→3→1→1→1)
    
    Input: grid = [[1,2,3],
                  [4,5,6]]
    Output: 12 (경로: 1→2→3→6)
    
    이동: 오른쪽 또는 아래쪽만 가능
    """
    pass
```

## 문제 4: 배낭 문제 (0/1 Knapsack) (Medium)
**시간 제한**: 35분

배낭의 용량이 주어지고, 각 물건의 무게와 가치가 주어졌을 때 최대 가치를 구하세요.

```python
def knapsack(capacity, weights, values):
    """
    예시:
    Input: capacity = 50, weights = [10, 20, 30], values = [60, 100, 120]
    Output: 220 (물건 2, 3을 선택: 20+30=50, 100+120=220)
    
    Input: capacity = 10, weights = [5, 4, 6, 3], values = [10, 40, 30, 50]
    Output: 90 (물건 2, 4를 선택: 4+3=7, 40+50=90)
    
    각 물건은 최대 1개만 선택 가능
    DP[i][w] = i번째까지 물건으로 무게 w일 때 최대 가치
    """
    pass
```

## 문제 5: 최장 증가 부분 수열 (LIS) (Medium)
**시간 제한**: 30분

배열에서 가장 긴 증가하는 부분 수열의 길이를 구하세요.

```python
def length_of_lis(nums):
    """
    예시:
    Input: nums = [10, 9, 2, 5, 3, 7, 101, 18]
    Output: 4 (LIS: [2, 3, 7, 101])
    
    Input: nums = [0, 1, 0, 3, 2, 3]
    Output: 4 (LIS: [0, 1, 2, 3])
    
    Input: nums = [7, 7, 7, 7, 7, 7, 7]
    Output: 1
    
    방법 1: DP - O(n²)
    방법 2: 이진 탐색 + DP - O(n log n)
    """
    pass
```

## 💡 DP의 핵심 개념

### 1. 최적 부분 구조 (Optimal Substructure)
- 큰 문제의 최적해가 작은 문제들의 최적해로 구성됨

### 2. 중복되는 부분 문제 (Overlapping Subproblems)
- 같은 하위 문제가 여러 번 계산됨
- 메모이제이션으로 해결

### 3. DP 접근법
- **Top-down (메모이제이션)**: 재귀 + 캐싱
- **Bottom-up (타뷸레이션)**: 반복문으로 테이블 채우기

## 🔧 백엔드 개발에서의 DP 활용

```python
# 시나리오 1: API 요청 최적화
def min_api_calls(requests, cache_capacity):
    """최소한의 API 호출로 모든 요청 처리 (캐시 활용)"""
    # 배낭 문제 변형
    pass

# 시나리오 2: 데이터베이스 쿼리 최적화
def min_query_cost(tables, join_costs):
    """테이블 조인 순서 최적화로 최소 비용 계산"""
    # 매트릭스 체인 곱셈 문제
    pass

# 시나리오 3: 리소스 할당 최적화
def optimize_server_allocation(servers, workloads):
    """서버 자원을 최적으로 할당하여 처리량 최대화"""
    # 배낭 문제 변형
    pass

# 시나리오 4: 캐시 교체 전략
def optimal_cache_replacement(access_pattern, cache_size):
    """미래 접근 패턴을 알 때 최적 캐시 교체"""
    # Longest Forward Distance (Belady's algorithm)
    pass
```

## 🎯 실전 문제 해결 전략

### 1. DP인지 판단하는 방법
- **최적화 문제**: 최대, 최소, 개수 구하기
- **중복 계산**: 같은 입력으로 여러 번 호출
- **선택의 여지**: 각 단계에서 여러 선택지 존재

### 2. DP 테이블 설계
```python
# 1차원 DP
dp = [0] * (n + 1)

# 2차원 DP
dp = [[0] * (m + 1) for _ in range(n + 1)]

# 딕셔너리 (메모이제이션)
memo = {}
```

### 3. 점화식 세우기
1. **상태 정의**: dp[i]가 무엇을 의미하는지
2. **초기값 설정**: 베이스 케이스
3. **전이 관계**: dp[i]를 이전 상태들로 표현
4. **최종 답**: 어느 위치에 답이 저장되는지

## ⚡ 최적화 팁

### 공간 복잡도 최적화
```python
# 2D DP를 1D로 줄이기 (롤링 배열)
def optimized_dp(n, m):
    # prev = [0] * (m + 1)
    curr = [0] * (m + 1)
    # 매 행마다 prev와 curr 교환
```

### 시간 복잡도 개선
```python
# 상태 전이 최적화
# O(n²) → O(n log n) (이진 탐색 활용)
```

## 🚨 주의사항
- **메모리 초과**: 큰 입력에서는 공간 최적화 필수
- **오버플로우**: 큰 수 계산 시 modulo 연산
- **초기값**: 잘못된 초기값은 전체 결과에 영향
- **인덱스**: 0-based vs 1-based 인덱싱 주의

한국 기업에서 DP는 중급 이상 문제로 자주 출제되니 꼭 마스터하세요!