# DFS와 BFS 탐색 알고리즘

## 문제 1: 이진 트리 최대 깊이 (Easy)
**시간 제한**: 15분

이진 트리의 최대 깊이를 구하세요.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_depth(root):
    """
    예시:
    Input: root = [3, 9, 20, null, null, 15, 7]
           3
          / \
         9  20
           /  \
          15   7
    Output: 3
    
    DFS 재귀와 BFS 반복 두 가지 방법으로 풀어보세요
    """
    pass
```

## 문제 2: 섬의 개수 (Medium)
**시간 제한**: 25분

2D 그리드에서 섬의 개수를 구하세요. '1'은 땅, '0'은 물입니다.

```python
def num_islands(grid):
    """
    예시:
    Input: grid = [
        ["1","1","1","1","0"],
        ["1","1","0","1","0"],
        ["1","1","0","0","0"],
        ["0","0","0","0","0"]
    ]
    Output: 1
    
    Input: grid = [
        ["1","1","0","0","0"],
        ["1","1","0","0","0"],
        ["0","0","1","0","0"],
        ["0","0","0","1","1"]
    ]
    Output: 3
    
    DFS나 BFS로 연결된 땅을 모두 방문하세요
    """
    pass
```

## 문제 3: 단어 찾기 (Hard)
**시간 제한**: 35분

2D 보드에서 주어진 단어가 존재하는지 확인하세요. 백트래킹(DFS) 사용.

```python
def exist(board, word):
    """
    예시:
    Input: board = [["A","B","C","E"],
                   ["S","F","C","S"],
                   ["A","D","E","E"]], word = "ABCCED"
    Output: True
    
    Input: board = [["A","B","C","E"],
                   ["S","F","C","S"],
                   ["A","D","E","E"]], word = "SEE"
    Output: True
    
    Input: board = [["A","B","C","E"],
                   ["S","F","C","S"],
                   ["A","D","E","E"]], word = "ABCB"
    Output: False
    
    규칙: 같은 셀을 두 번 사용할 수 없습니다
    """
    pass
```

## 문제 4: 최단 경로 길이 (Medium)
**시간 제한**: 30분

BFS를 사용하여 2D 그리드에서 최단 경로를 찾으세요.

```python
from collections import deque

def shortest_path_binary_matrix(grid):
    """
    예시:
    Input: grid = [[0,0,1],
                  [1,1,0],
                  [0,0,0]]
    Output: 4 (경로: (0,0) -> (0,1) -> (1,2) -> (2,2))
    
    Input: grid = [[0,1],
                  [1,0]]
    Output: -1 (경로 없음)
    
    규칙: 
    - 0은 지나갈 수 있고, 1은 막혀있습니다
    - 8방향으로 이동 가능 (대각선 포함)
    - (0,0)에서 (n-1,n-1)까지의 최단 경로
    """
    pass
```

## 문제 5: 전화번호 문자 조합 (Medium)
**시간 제한**: 30분

전화번호 숫자가 주어졌을 때 가능한 모든 문자 조합을 구하세요.

```python
def letter_combinations(digits):
    """
    예시:
    Input: digits = "23"
    Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]
    
    Input: digits = ""
    Output: []
    
    Input: digits = "2"
    Output: ["a","b","c"]
    
    전화기 키패드:
    2: abc, 3: def, 4: ghi, 5: jkl, 
    6: mno, 7: pqrs, 8: tuv, 9: wxyz
    
    백트래킹 DFS로 모든 조합 생성
    """
    pass
```

## 💡 백엔드 개발자를 위한 학습 포인트

### DFS (깊이 우선 탐색)
- **특징**: 재귀, 스택, 메모리 효율적
- **활용**: 파일 시스템 탐색, 의존성 분석, 백트래킹

### BFS (너비 우선 탐색)
- **특징**: 큐, 최단 경로, 레벨 순회
- **활용**: 소셜 네트워크 분석, 웹 크롤링, 최단 경로

## 🔧 실제 백엔드 시나리오

```python
# 시나리오 1: 파일 시스템 검색
def find_files_by_extension(directory, extension):
    """특정 확장자 파일들을 DFS로 찾기"""
    pass

# 시나리오 2: 사용자 관계망 분석
def find_mutual_friends(user_id, target_id, max_degree=3):
    """BFS로 상호 친구 찾기 (3단계 이내)"""
    pass

# 시나리오 3: API 의존성 그래프
def detect_circular_dependency(services):
    """DFS로 서비스 간 순환 의존성 탐지"""
    pass

# 시나리오 4: 캐시 무효화 전파
def invalidate_dependent_caches(cache_key):
    """BFS로 의존성 있는 캐시들 무효화"""
    pass
```

## 🌐 네트워크/분산 시스템 관점

### 그래프 구조의 실제 활용
- **마이크로서비스**: 서비스 의존성 그래프
- **데이터베이스**: 외래키 관계, 인덱스 트리
- **캐시 시스템**: 캐시 의존성 그래프
- **로드 밸런서**: 서버 health check 그래프

### 탐색 전략
- **DFS**: 깊은 분석 필요시 (로그 분석, 에러 추적)
- **BFS**: 넓은 범위 탐색 (장애 전파 분석, 영향도 분석)

## ⚡ 성능 최적화

### 메모리 관리
```python
# DFS - 재귀 깊이 제한
import sys
sys.setrecursionlimit(10000)

# BFS - 큐 크기 관리
from collections import deque
queue = deque(maxlen=10000)
```

### 방문 처리 최적화
```python
# 셋 사용으로 O(1) 검색
visited = set()

# 그리드의 경우 인덱스로 직접 표시
grid[i][j] = '#'  # 방문 표시
```

## 🎯 실전 팁
- **시간 복잡도**: V + E (정점 + 간선)
- **공간 복잡도**: 재귀 스택 vs 큐 메모리
- **순환 탐지**: visited 배열 필수
- **백트래킹**: 탐색 후 상태 복원