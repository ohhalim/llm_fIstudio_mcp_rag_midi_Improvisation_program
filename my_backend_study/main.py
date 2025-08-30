from fastapi import FastAPI

app = FastAPI(
    titie="나의 첫 백엔드 api",
    description="fastapi로 배우는 백엔드 개발",
    version= "1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "안녕"}

@app.get("/hello/{name}")
def say_hello(name:str):
    return {"message": f"안녕하세요"}

@app.get("/add")
def add_numbers(a: int, b: int):
    result = a + b 
    return {
        "a": a,
        "b": b,
        "result": result,
        "operation": "덧셈"
    }
