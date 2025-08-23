# 정렬과 탐색 알고리즘

## 문제 1: 이진 탐색 (Easy)
**시간 제한**: 15분

정렬된 배열에서 target 값의 인덱스를 찾으세요. 없으면 -1을 반환하세요.

```python
def binary_search(nums, target):
    """
    예시:
    Input: nums = [-1, 0, 3, 5, 9, 12], target = 9
    Output: 4
    
    Input: nums = [-1, 0, 3, 5, 9, 12], target = 2
    Output: -1
    
    시간복잡도: O(log n)
    공간복잡도: O(1)
    """
    pass
```

## 문제 2: 첫 번째와 마지막 위치 찾기 (Medium)
**시간 제한**: 25분

정렬된 배열에서 target 값이 처음과 마지막에 나타나는 위치를 찾으세요.

```python
def search_range(nums, target):
    """
    예시:
    Input: nums = [5, 7, 7, 8, 8, 10], target = 8
    Output: [3, 4]
    
    Input: nums = [5, 7, 7, 8, 8, 10], target = 6
    Output: [-1, -1]
    
    Input: nums = [], target = 0
    Output: [-1, -1]
    
    시간복잡도: O(log n) (이진탐색 2번)
    """
    pass
```

## 문제 3: 회전된 정렬 배열에서 탐색 (Medium)
**시간 제한**: 30분

회전된 정렬 배열에서 target을 찾으세요. 한국 기업에서 자주 출제됩니다!

```python
def search_rotated_array(nums, target):
    """
    예시:
    Input: nums = [4, 5, 6, 7, 0, 1, 2], target = 0
    Output: 4
    
    Input: nums = [4, 5, 6, 7, 0, 1, 2], target = 3
    Output: -1
    
    Input: nums = [1], target = 0
    Output: -1
    
    힌트: 배열의 한쪽은 항상 정렬되어 있습니다
    시간복잡도: O(log n)
    """
    pass
```

## 문제 4: K번째로 큰 원소 (Medium)
**시간 제한**: 30분

배열에서 K번째로 큰 원소를 찾으세요. (중복 포함)

```python
def find_kth_largest(nums, k):
    """
    예시:
    Input: nums = [3, 2, 1, 5, 6, 4], k = 2
    Output: 5
    
    Input: nums = [3, 2, 3, 1, 2, 4, 5, 5, 6], k = 4
    Output: 4
    
    방법 1: 정렬 - O(n log n)
    방법 2: 힙 - O(n log k)
    방법 3: 퀵셀렉트 - 평균 O(n)
    """
    pass
```

## 문제 5: 색깔별 정렬 (Dutch Flag) (Medium)
**시간 제한**: 25분

0, 1, 2로만 구성된 배열을 정렬하세요. 추가 공간 사용 없이 한 번의 패스로 해결하세요.

```python
def sort_colors(nums):
    """
    예시:
    Input: nums = [2, 0, 2, 1, 1, 0]
    Output: [0, 0, 1, 1, 2, 2]
    
    Input: nums = [2, 0, 1]
    Output: [0, 1, 2]
    
    네덜란드 국기 문제로 유명합니다
    시간복잡도: O(n), 공간복잡도: O(1)
    """
    # nums를 직접 수정하세요 (in-place)
    pass
```

## 💡 백엔드 개발자를 위한 학습 포인트

### 이진 탐색의 활용
- **데이터베이스**: B+ Tree 인덱스
- **API**: 페이지네이션에서 효율적 탐색
- **로그 분석**: 시간 기반 로그 검색
- **캐싱**: 캐시 만료 시간 검색

### 정렬 알고리즘 선택
- **QuickSort**: 평균 성능 좋음, 메모리 효율적
- **MergeSort**: 안정 정렬, 최악의 경우에도 O(n log n)
- **HeapSort**: 추가 메모리 불필요, 우선순위 큐

## 🔧 실제 백엔드 시나리오

```python
# 시나리오 1: API 응답 시간 분석
def find_slow_requests(response_times, threshold):
    """response_times 중에서 threshold 이상인 첫 번째 요청을 찾기"""
    # 이진 탐색 활용
    pass

# 시나리오 2: 사용자 랭킹 시스템
def get_user_rank(scores, user_score):
    """정렬된 점수 배열에서 사용자의 랭킹 계산"""
    # 이진 탐색으로 위치 찾기
    pass

# 시나리오 3: 로그 레벨별 분류
def categorize_logs(logs):
    """ERROR(2), WARN(1), INFO(0) 로그를 분류"""
    # Dutch Flag 알고리즘 활용
    pass
```

## ⚡ 성능 최적화 팁
- **이진 탐색**: 정렬된 데이터에서는 항상 고려
- **정렬 선택**: 데이터 특성에 따라 알고리즘 선택
- **인메모리 vs 디스크**: 대용량 데이터 처리 시 외부 정렬 고려
- **캐싱**: 반복되는 탐색 결과는 캐시에 저장