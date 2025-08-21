# Music AI 마이크로서비스 아키텍처

FastAPI 기반의 음악 AI 마이크로서비스 시스템입니다. MIDI 처리, 즉흥연주 생성, RAG 기반 음악 이론 검색 기능을 제공합니다.

## 아키텍처 개요

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   User Service   │    │  MIDI Service   │
│    (Port 8000)  │    │   (Port 8001)    │    │  (Port 8002)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   RAG Service   │    │   PostgreSQL     │    │      Redis      │
│   (Port 8003)   │    │   (Port 5432)    │    │   (Port 6379)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 서비스 구성

### 1. API Gateway (Port 8000)
- 모든 외부 요청의 진입점
- 인증 및 라우팅 관리
- 마이크로서비스 간 통신 조정

### 2. User Service (Port 8001)
- 사용자 관리 (등록, 로그인, 프로필)
- JWT 기반 인증
- 사용자 선호도 관리

### 3. MIDI Service (Port 8002)
- MIDI 파일 업로드 및 분석
- 화성 분석, 코드 진행 추출
- AI 기반 즉흥연주 생성

### 4. RAG Service (Port 8003)
- 음악 이론 문서 관리
- ChromaDB 기반 벡터 검색
- OpenAI GPT를 통한 질의응답

## 주요 기능

### 🎵 MIDI 처리
- MIDI 파일 업로드 및 메타데이터 추출
- 화성 분석 (코드 진행, 키 시그니처)
- 악기 분석 및 트랙 정보

### 🎹 즉흥연주 생성
- 기존 MIDI 파일 기반 즉흥연주
- 다양한 음악 스타일 지원 (재즈, 블루스 등)
- 복잡도 및 길이 조절 가능

### 📚 RAG 기반 음악 이론 검색
- 음악 이론 문서 벡터화 및 저장
- 자연어 질의를 통한 검색
- AI 기반 상세 답변 생성

### 👤 사용자 관리
- 회원가입 및 로그인
- 개인화된 음악 선호도 설정
- 업로드한 파일 및 생성 기록 관리

## 기술 스택

### Backend
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **Pydantic**: 데이터 검증 및 직렬화
- **PostgreSQL**: 주 데이터베이스
- **Redis**: 캐싱 및 세션 관리

### MIDI 처리
- **Mido**: MIDI 파일 처리
- **python-rtmidi**: 실시간 MIDI 처리
- **NumPy**: 수치 계산

### AI/ML
- **OpenAI GPT**: 자연어 생성
- **Sentence Transformers**: 텍스트 임베딩
- **ChromaDB**: 벡터 데이터베이스
- **LangChain**: RAG 구현

### 인프라
- **Docker**: 컨테이너화
- **Docker Compose**: 오케스트레이션
- **Prometheus**: 모니터링 (선택사항)
- **Grafana**: 대시보드 (선택사항)

## 빠른 시작

### 1. 사전 준비
```bash
# 저장소 클론
git clone <repository-url>
cd llm_fIstudio_mcp_rag_midi_Improvisation_program

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 입력
```

### 2. 환경 변수 설정
`.env` 파일에서 다음 항목들을 설정하세요:

```bash
# 필수 설정
AUTH_SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=your-openai-api-key

# 데이터베이스 (기본값 사용 가능)
DB_DATABASE_URL=postgresql://musicuser:musicpass@postgres:5432/musicdb
REDIS_REDIS_URL=redis://redis:6379
```

### 3. Docker Compose로 실행
```bash
# 전체 시스템 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 모니터링과 함께 시작 (선택사항)
docker-compose --profile monitoring up -d
```

### 4. 서비스 확인
- API Gateway: http://localhost:8000
- API 문서: http://localhost:8000/docs
- User Service: http://localhost:8001/docs
- MIDI Service: http://localhost:8002/docs
- RAG Service: http://localhost:8003/docs

## API 사용법

### 1. 사용자 등록 및 로그인
```bash
# 회원가입
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "full_name": "Test User"
  }'

# 로그인
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "testpassword123"
  }'
```

### 2. MIDI 파일 업로드
```bash
# 토큰을 받은 후 MIDI 파일 업로드
curl -X POST "http://localhost:8000/api/midi/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/your/midi/file.mid" \
  -F "title=My MIDI File" \
  -F "genre=Jazz"
```

### 3. 즉흥연주 생성
```bash
# 업로드된 MIDI 파일을 기반으로 즉흥연주 생성
curl -X POST "http://localhost:8000/api/midi/generate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "improvisation",
    "source_midi_id": 1,
    "style": "jazz",
    "duration": 30,
    "complexity": "medium"
  }'
```

### 4. RAG 문서 업로드 및 질의
```bash
# 음악 이론 문서 업로드
curl -X POST "http://localhost:8000/api/rag/documents" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "title=Jazz Harmony Basics" \
  -F "content=Jazz harmony is based on extended chords..." \
  -F "document_type=music_theory" \
  -F "category=harmony"

# 질의응답
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "재즈 화성에서 2-5-1 진행이란 무엇인가요?",
    "max_results": 5
  }'
```

## 개발 환경 설정

### 로컬 개발
```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개별 서비스 실행 (개발 모드)
cd services/gateway && python main.py
cd services/user-service && python main.py
cd services/midi-service && python main.py
cd services/rag-service && python main.py
```

### 데이터베이스 마이그레이션
```bash
# 데이터베이스 초기화 (개발환경)
docker-compose up -d postgres redis

# 각 서비스에서 자동으로 테이블 생성됨
# 또는 수동으로 Alembic 사용 가능
```

## 모니터링

### Prometheus & Grafana (선택사항)
```bash
# 모니터링 스택 시작
docker-compose --profile monitoring up -d

# 접속
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

### 헬스 체크
```bash
# 모든 서비스 상태 확인
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## 문제 해결

### 일반적인 문제
1. **포트 충돌**: 다른 서비스가 포트를 사용중인 경우 docker-compose.yml에서 포트 변경
2. **메모리 부족**: ChromaDB와 AI 모델로 인해 최소 4GB RAM 권장
3. **OpenAI API 키**: RAG 서비스 사용 시 유효한 API 키 필요

### 로그 확인
```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs gateway
docker-compose logs user-service
docker-compose logs midi-service
docker-compose logs rag-service
```

### 컨테이너 재시작
```bash
# 전체 재시작
docker-compose restart

# 특정 서비스 재시작
docker-compose restart gateway
```

## 확장 계획

- [ ] WebSocket을 통한 실시간 MIDI 생성
- [ ] 더 정교한 음악 이론 분석
- [ ] 머신러닝 기반 스타일 분류
- [ ] 다중 사용자 협업 기능
- [ ] 외부 DAW 연동

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request