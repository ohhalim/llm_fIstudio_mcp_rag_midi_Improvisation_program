# Music AI 마이크로서비스 개발/배포 도구

# 기본 설정
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = music-ai

# Docker Compose 명령어들
.PHONY: help build up down restart logs clean dev test

help: ## 사용 가능한 명령어 표시
	@echo "Music AI 마이크로서비스 관리 도구"
	@echo ""
	@echo "사용 가능한 명령어:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Docker 이미지 빌드
	@echo "🔨 Docker 이미지 빌드 중..."
	docker-compose build

up: ## 전체 서비스 시작
	@echo "🚀 서비스 시작 중..."
	docker-compose up -d
	@echo "✅ 서비스가 시작되었습니다!"
	@echo "API Gateway: http://localhost:8000"
	@echo "API 문서: http://localhost:8000/docs"

up-dev: ## 개발 모드로 서비스 시작 (로그 출력)
	@echo "🔧 개발 모드로 서비스 시작 중..."
	docker-compose up

up-monitoring: ## 모니터링과 함께 서비스 시작
	@echo "📊 모니터링과 함께 서비스 시작 중..."
	docker-compose --profile monitoring up -d
	@echo "✅ 모니터링 서비스가 시작되었습니다!"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000 (admin/admin)"

down: ## 전체 서비스 중지
	@echo "🛑 서비스 중지 중..."
	docker-compose down

down-v: ## 전체 서비스 중지 및 볼륨 삭제
	@echo "🗑️ 서비스 중지 및 볼륨 삭제 중..."
	docker-compose down -v

restart: ## 전체 서비스 재시작
	@echo "🔄 서비스 재시작 중..."
	docker-compose restart

restart-gateway: ## API Gateway 재시작
	docker-compose restart gateway

restart-user: ## User Service 재시작
	docker-compose restart user-service

restart-midi: ## MIDI Service 재시작
	docker-compose restart midi-service

restart-rag: ## RAG Service 재시작
	docker-compose restart rag-service

logs: ## 전체 서비스 로그 확인
	docker-compose logs -f

logs-gateway: ## Gateway 로그 확인
	docker-compose logs -f gateway

logs-user: ## User Service 로그 확인
	docker-compose logs -f user-service

logs-midi: ## MIDI Service 로그 확인
	docker-compose logs -f midi-service

logs-rag: ## RAG Service 로그 확인
	docker-compose logs -f rag-service

status: ## 서비스 상태 확인
	@echo "📋 서비스 상태:"
	docker-compose ps

health: ## 헬스 체크
	@echo "🏥 헬스 체크 수행 중..."
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Gateway: Healthy" || echo "❌ Gateway: Unhealthy"
	@curl -f http://localhost:8001/health 2>/dev/null && echo "✅ User Service: Healthy" || echo "❌ User Service: Unhealthy"
	@curl -f http://localhost:8002/health 2>/dev/null && echo "✅ MIDI Service: Healthy" || echo "❌ MIDI Service: Unhealthy"
	@curl -f http://localhost:8003/health 2>/dev/null && echo "✅ RAG Service: Healthy" || echo "❌ RAG Service: Unhealthy"

clean: ## 사용하지 않는 Docker 리소스 정리
	@echo "🧹 Docker 리소스 정리 중..."
	docker system prune -f
	docker volume prune -f

clean-all: ## 모든 Docker 리소스 정리 (주의!)
	@echo "⚠️ 모든 Docker 리소스 정리 중... (위험한 작업입니다!)"
	@read -p "정말로 계속하시겠습니까? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -a -f --volumes; \
	else \
		echo "작업이 취소되었습니다."; \
	fi

# 개발 환경
setup-dev: ## 개발 환경 설정
	@echo "🔧 개발 환경 설정 중..."
	cp .env.example .env
	@echo "✅ .env 파일이 생성되었습니다. 필요한 설정을 편집하세요."
	@echo "🔑 특히 OPENAI_API_KEY와 AUTH_SECRET_KEY를 설정해주세요."

install-deps: ## Python 의존성 설치 (로컬 개발용)
	@echo "📦 Python 의존성 설치 중..."
	pip install -r requirements.txt

run-local: ## 로컬에서 개별 서비스 실행 (개발용)
	@echo "🏃 로컬 개발 모드 실행 안내:"
	@echo "1. 데이터베이스 서비스 먼저 시작: make up-db"
	@echo "2. 각 서비스를 별도 터미널에서 실행:"
	@echo "   cd services/gateway && python main.py"
	@echo "   cd services/user-service && python main.py"
	@echo "   cd services/midi-service && python main.py"
	@echo "   cd services/rag-service && python main.py"

up-db: ## 데이터베이스만 시작 (로컬 개발용)
	@echo "🗄️ 데이터베이스 서비스 시작 중..."
	docker-compose up -d postgres redis

# 테스트
test: ## 테스트 실행
	@echo "🧪 테스트 실행 중..."
	pytest tests/ -v

test-coverage: ## 커버리지와 함께 테스트 실행
	@echo "📊 커버리지 테스트 실행 중..."
	pytest tests/ --cov=services --cov-report=html

# 배포
deploy-prod: ## 프로덕션 배포 (환경 변수 확인 필요)
	@echo "🚀 프로덕션 배포 중..."
	@echo "⚠️ 프로덕션 환경 변수가 올바르게 설정되었는지 확인하세요!"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 유틸리티
shell-gateway: ## Gateway 컨테이너 셸 접속
	docker-compose exec gateway /bin/bash

shell-user: ## User Service 컨테이너 셸 접속
	docker-compose exec user-service /bin/bash

shell-midi: ## MIDI Service 컨테이너 셸 접속
	docker-compose exec midi-service /bin/bash

shell-rag: ## RAG Service 컨테이너 셸 접속
	docker-compose exec rag-service /bin/bash

shell-db: ## PostgreSQL 컨테이너 접속
	docker-compose exec postgres psql -U musicuser -d musicdb

backup-db: ## 데이터베이스 백업
	@echo "💾 데이터베이스 백업 중..."
	docker-compose exec postgres pg_dump -U musicuser musicdb > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ 백업 완료: backup_$(shell date +%Y%m%d_%H%M%S).sql"

docs: ## API 문서 열기
	@echo "📖 API 문서 열기..."
	@which open >/dev/null && open http://localhost:8000/docs || echo "브라우저에서 http://localhost:8000/docs 를 열어주세요"