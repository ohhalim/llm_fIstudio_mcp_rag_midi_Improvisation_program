# RESTful API 서버 - 백엔드 취업 준비용

FastAPI와 PostgreSQL을 사용한 실무 중심 RESTful API 서버입니다.

## 🎯 프로젝트 목적

백엔드 개발자 취업을 위한 실무 역량 강화:
- JWT 기반 인증 시스템 구현
- CRUD 게시판 API 개발
- 파일 업로드/다운로드 시스템
- 페이징 및 검색 기능
- 보안 및 성능 최적화

## 🚀 주요 기능

### 1. 인증 시스템
- **회원가입/로그인**: 이메일 기반 사용자 등록
- **JWT 토큰**: 안전한 인증 토큰 발급 및 검증
- **비밀번호 암호화**: BCrypt를 사용한 안전한 비밀번호 저장

### 2. 게시판 기능  
- **CRUD 작업**: 게시글 생성, 조회, 수정, 삭제
- **권한 관리**: 본인 작성 게시글만 수정/삭제 가능
- **페이징**: 효율적인 대용량 데이터 처리
- **검색**: 제목/내용 기반 검색 기능

### 3. 파일 관리
- **파일 업로드**: 단일/다중 파일 업로드 지원
- **파일 검증**: 크기 및 확장자 검사
- **게시글 연동**: 게시글과 파일 첨부 기능
- **다운로드**: 업로드된 파일 다운로드

## 🛠 기술 스택

- **Backend**: Python 3.9+, FastAPI
- **Database**: PostgreSQL, SQLAlchemy ORM
- **Authentication**: JWT, PassLib (BCrypt)
- **File Handling**: Async File Operations
- **Documentation**: Swagger/OpenAPI 자동 생성

## 📁 프로젝트 구조

```
restful-api-server/
├── app/
│   ├── api/                # API 엔드포인트
│   │   ├── auth.py         # 인증 관련 API
│   │   ├── posts.py        # 게시판 API
│   │   └── upload.py       # 파일 업로드 API
│   ├── core/               # 핵심 설정
│   │   ├── config.py       # 환경 설정
│   │   ├── security.py     # 보안 관련 함수
│   │   ├── deps.py         # 의존성 주입
│   │   └── file_utils.py   # 파일 유틸리티
│   ├── crud/               # 데이터베이스 작업
│   │   ├── user.py         # 사용자 CRUD
│   │   └── post.py         # 게시글 CRUD
│   ├── db/                 # 데이터베이스 설정
│   │   └── database.py     # DB 연결 및 세션
│   ├── models/             # 데이터베이스 모델
│   │   ├── user.py         # 사용자 모델
│   │   └── post.py         # 게시글 모델
│   ├── schemas/            # Pydantic 스키마
│   │   ├── user.py         # 사용자 스키마
│   │   └── post.py         # 게시글 스키마
│   └── main.py             # FastAPI 앱
├── uploads/                # 업로드된 파일 저장
├── requirements.txt        # Python 의존성
├── .env                    # 환경 변수
└── server.py              # 서버 시작점
```

## 🚀 시작하기

### 1. 의존성 설치

```bash
# 파이썬 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

PostgreSQL을 설치하고 데이터베이스를 생성합니다:

```sql
-- PostgreSQL에서 실행
CREATE DATABASE restful_api_db;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE restful_api_db TO your_username;
```

### 3. 환경 변수 설정

`.env` 파일을 수정하여 데이터베이스 연결 정보를 설정합니다:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/restful_api_db
SECRET_KEY=your-very-secure-secret-key-here
```

### 4. 서버 실행

```bash
# 개발 서버 시작
python server.py

# 또는
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API 사용법

서버 시작 후 다음 주소에서 API 문서를 확인할 수 있습니다:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 주요 엔드포인트

#### 인증
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인
- `GET /api/v1/auth/me` - 내 정보 조회

#### 게시판
- `GET /api/v1/posts/` - 게시글 목록 (페이징, 검색)
- `POST /api/v1/posts/` - 게시글 작성 (인증 필요)
- `GET /api/v1/posts/{id}` - 게시글 상세 조회
- `PUT /api/v1/posts/{id}` - 게시글 수정 (인증 필요)
- `DELETE /api/v1/posts/{id}` - 게시글 삭제 (인증 필요)

#### 파일 업로드
- `POST /api/v1/files/upload` - 파일 업로드 (인증 필요)
- `POST /api/v1/files/upload-multiple` - 다중 파일 업로드
- `GET /api/v1/files/download/{path}` - 파일 다운로드

## 🔧 주요 학습 포인트

### 1. JWT 인증 시스템
```python
# 토큰 생성 예제
access_token = create_access_token(
    data={"sub": user.email}, 
    expires_delta=timedelta(minutes=30)
)
```

### 2. 데이터베이스 관계
```python
# 일대다 관계 설정
class Post(Base):
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
```

### 3. 페이징 구현
```python
# 효율적인 페이징
skip = (page - 1) * size
posts = query.offset(skip).limit(size).all()
total = query.count()
```

### 4. 파일 업로드 보안
```python
# 파일 유효성 검사
ALLOWED_EXTENSIONS = {'.jpg', '.png', '.pdf', '.docx'}
if file_extension not in ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail="허용되지 않는 파일")
```

## 🔒 보안 기능

- **비밀번호 해싱**: BCrypt를 사용한 안전한 비밀번호 저장
- **JWT 토큰**: 상태없는(stateless) 인증
- **파일 검증**: 업로드 파일 크기 및 확장자 제한
- **CORS 정책**: 허용된 도메인만 접근 가능
- **입력 검증**: Pydantic을 통한 자동 데이터 검증

## 🧪 테스트

```bash
# 테스트 실행 (구현 예정)
pytest tests/
```

## 📈 성능 최적화

- **데이터베이스 인덱싱**: 검색 성능 향상
- **N+1 쿼리 방지**: joinedload를 사용한 관계 데이터 로드
- **비동기 파일 처리**: aiofiles를 사용한 비동기 I/O
- **페이징**: 대용량 데이터 효율적 처리

## 🚀 배포 준비

### Docker 사용 (구현 예정)
```dockerfile
FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 환경별 설정
- **개발**: DEBUG=True, 상세 로깅
- **운영**: DEBUG=False, 보안 강화

## 📚 추가 학습 자료

1. **FastAPI 공식 문서**: https://fastapi.tiangolo.com/
2. **SQLAlchemy 문서**: https://docs.sqlalchemy.org/
3. **JWT 이해하기**: https://jwt.io/
4. **PostgreSQL 최적화**: https://www.postgresql.org/docs/

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 📝 라이선스

MIT License - 자유롭게 사용하세요.

---

**백엔드 개발자로의 첫 걸음을 응원합니다! 🚀**