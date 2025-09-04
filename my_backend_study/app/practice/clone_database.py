# 데이터베이스 엔진 생성
from sqlalchemy import create_engine
# 모델 베이스 클래스 생성
from sqlalchemy.ext.declarative import declarative_base
# 세션 팩토리 생성
from sqlalchemy.orm import sessionmaker
# config에서 설정 가져오기
from .config import settings


engine =create_engine(
    # config에서 생성한 데이터베이스 연결 URL사용
    settings.database_url,
    # 디버그 모드일떄 SQL 쿼리 로깅
    echo=settings.DEBUG,
    # 연결풀에서 연결을 사용하기 전에 ping으로 유효성 확인
    pool_pre_ping=True,
)

# 자동 커밋 비활성솨// 자동flush비활성화 / 생성한 엔진과 바인딩
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 데이터베이스모델이 상속받을 베이스 클래스 생성
Base = declarative_base()

# 각 요청마다 새로운 데이터베이스 세션 생성
def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# 모든 모델의 테이블을 데이터 베이스 생성
def create_tables():
    Base.metadata.create_all(bind=engine)    