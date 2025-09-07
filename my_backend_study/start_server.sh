#!/bin/bash

# FastAPI 서버 시작 스크립트
echo "Gemini Chat API 서버를 시작합니다..."

# uvicorn 실행 (sys.path가 main.py에서 자동 설정됨)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

echo "서버가 http://127.0.0.1:8001 에서 실행 중입니다."
echo "API 문서: http://127.0.0.1:8001/docs"