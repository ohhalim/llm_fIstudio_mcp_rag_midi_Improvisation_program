"""
데이터베이스 연결 및 세션 관리 모듈
PostgreSQL 데이터베이스와의 연결을 설정하고 SQLAlchemy 세션을 관리합니다.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# PostgreSQL 데이터베이스 엔진 생성
# echo=True로 설정하면 SQL 쿼리를 콘솔에 출력해서 디버깅에 도움됨
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # 개발 중에는 SQL 로그 출력
)

# 데이터베이스 세션 팩토리 생성
# autocommit=False: 명시적으로 commit해야 변경사항이 저장됨
# autoflush=False: 자동으로 flush하지 않음 (수동 제어)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 모든 데이터베이스 모델의 베이스 클래스
# 이 클래스를 상속받아서 테이블 모델을 만들 예정
Base = declarative_base()

def get_db():
    """
    데이터베이스 세션을 생성하고 반환하는 의존성 함수
    FastAPI의 Dependency Injection에서 사용됩니다.
    
    사용법:
    @app.get("/users/")
    def get_users(db: Session = Depends(get_db)):
        return crud.get_users(db)
    """
    db = SessionLocal()
    try:
        # 요청이 처리되는 동안 데이터베이스 세션 제공
        yield db
    finally:
        # 요청이 끝나면 세션을 자동으로 닫음 (메모리 누수 방지)
        db.close()