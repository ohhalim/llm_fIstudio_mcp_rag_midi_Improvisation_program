from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.database_url,
    echo=settings.DEBUG,  # SQL 쿼리 로깅 (개발 환경에서만)
    pool_pre_ping=True,
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()

def get_db():
    """
    데이터베이스 세션을 제공하는 제너레이터 함수
    FastAPI의 의존성 주입(Dependency Injection)에 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)