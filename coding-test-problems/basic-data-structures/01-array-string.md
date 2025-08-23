# 배열과 문자열 기본 문제

## 문제 1: 두 수의 합 (Easy)
**시간 제한**: 10분

주어진 정수 배열 `nums`와 정수 `target`이 있을 때, 두 수의 합이 `target`과 같은 인덱스 쌍을 반환하세요.

```python
def two_sum(nums, target):
    """
    예시:
    Input: nums = [2, 7, 11, 15], target = 9
    Output: [0, 1] (nums[0] + nums[1] = 2 + 7 = 9)
    
    Input: nums = [3, 2, 4], target = 6
    Output: [1, 2]
    """
    pass
```

## 문제 2: 문자열 뒤집기 (Easy)
**시간 제한**: 15분

문자열을 단어별로 뒤집되, 각 단어의 순서는 유지하세요.

```python
def reverse_words_in_string(s):
    """
    예시:
    Input: "Let's take LeetCode contest"
    Output: "s'teL ekat edoCteeL tsetnoc"
    
    Input: "God Ding"
    Output: "doG gniD"
    """
    pass
```

## 문제 3: 중복 제거 (Medium)
**시간 제한**: 20분

정렬된 배열에서 중복을 제거하고, 유니크한 원소들만 앞쪽으로 이동시키세요. 새로운 배열을 만들지 말고 기존 배열을 수정하세요.

```python
def remove_duplicates(nums):
    """
    예시:
    Input: nums = [1, 1, 2]
    Output: 2, nums = [1, 2, _]
    
    Input: nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
    Output: 5, nums = [0, 1, 2, 3, 4, _, _, _, _, _]
    
    Return: 유니크한 원소의 개수
    """
    pass
```

## 문제 4: 가장 긴 공통 접두사 (Medium)
**시간 제한**: 25분

문자열 배열에서 가장 긴 공통 접두사를 찾으세요.

```python
def longest_common_prefix(strs):
    """
    예시:
    Input: strs = ["flower", "flow", "flight"]
    Output: "fl"
    
    Input: strs = ["dog", "racecar", "car"]
    Output: ""
    
    Input: strs = ["interspecies", "interstellar", "interstate"]
    Output: "inters"
    """
    pass
```

## 💡 학습 포인트
- 배열 인덱싱과 슬라이싱
- 문자열 메서드 활용
- 투 포인터 테크닉
- 해시맵 활용법
- 시간복잡도 최적화