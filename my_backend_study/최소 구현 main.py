from fastapi import FastAPI

# fastapi클래스의 인스턴스를 생성하여 app 변수에 할당 
app = FastAPI()
# app = FastAPI(
#     title="나의 첫 백엔드 api",
#     description="fastapi로 배우는 백엔드 개발",
#     version= "1.0.0"
# )

#데코레이터를 사용, 아래 정의된 함수를 http get 요청에 대한 핸들러로 등록
# 이 데코레이터는 url 경로 ("/")로 들어오는 get 요청을 read_root 함수와 연결하여 
# 해당경로로 요청이 들어왔을때 이 함수가 실행되도록 한다
@app.get("/")
# read_root 함수를 정의 이 함수는 어떤 매개변수도 받지 않음
# 기본경로("/")로 get 요청이 들어왔을때 실행될 코드
def read_root():
    # 딕셔너리 json응답 반환
    return {"message": "안녕"}
# {name}은 경로 매개변수가 된다 
# 예를들어 /hello/john 요청이 들어오면 john이 name 변수에 전당 
@app.get("/hello/{name}")
def say_hello(name:str):
    return {"message": f"안녕하세요, {name}님!"}

@app.get("/add")
# a,b 라는 정수타입의 매개변수를 받는다 
# 이 함수는 덧셈연산을 수행하는 api로직을 정의
# 클라이언트가 요청시 전달하는 두개의 숫자를 받아 처리
def add_numbers(a: int, b: int):
    # a, b를 더하여 그결과를 result 변수에 할당
    result = a + b 
    return {
        "a": a,
        "b": b,
        "result": result,
        "operation": "덧셈"
    }

#   지금 배운 것들:
#   - @app.get() : GET 요청을 받는 방법
#   - {name} : URL에서 값을 받는 방법 (Path Parameter)
#   - ?a=5&b=3 : 쿼리 파라미터로 값을 받는 방법
#   - 자동 API 문서 생성 (/docs)


# 최소구현 api
# from fastapi import FastAPI

# app= FastAPI()

# @app.get("/")
# def hello():
#     return {"message": "Hello World"}