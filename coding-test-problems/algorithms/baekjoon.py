11720번

N = int(input())

numbers = input().strip()

total = 0

for i in range(N):
    total += int(numbers[i])

print(total)

# 코드 설명:
# N = int(input()): 숫자의 개수 N을 입력받습니다.
# numbers = input().strip(): N개의 숫자가 공백 없이 주어진 문자열을 입력받습니다.
# total = 0: 합계를 저장할 변수를 초기화합니다.
# for i in range(N): N번 반복하면서 각 숫자를 처리합니다.
# total += int(numbers[i]): 문자열의 i번째 문자를 정수로 변환하여 합계에 더합니다.
# print(total): 최종 합계를 출력합니다.