"""
database.py - PostgreSQL 데이터베이스 연결 및 설정

이 파일에서 배울 수 있는 개념들:
1. SQLAlchemy 2.0 비동기 엔진 설정
2. 데이터베이스 연결 풀 관리
3. 세션 팩토리 패턴
4. 컨텍스트 매니저를 통한 자동 세션 관리
5. 데이터베이스 헬스체크
6. 트랜잭션 관리
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from config import settings
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy 모델들의 기본 클래스
Base = declarative_base()

# 전역 변수들
async_engine = None
async_session_factory = None
sync_engine = None
sync_session_factory = None


def create_database_engines():
    """
    데이터베이스 엔진들을 생성합니다.
    
    비동기와 동기 엔진을 모두 생성하여 다양한 상황에서 사용할 수 있도록 합니다.
    - 비동기 엔진: FastAPI의 비동기 엔드포인트에서 사용
    - 동기 엔진: 마이그레이션, 스크립트, 일부 백그라운드 작업에서 사용
    """
    global async_engine, async_session_factory, sync_engine, sync_session_factory
    
    try:
        # 비동기 엔진 생성 (주 사용)
        async_engine = create_async_engine(
            settings.database_url,
            
            # 연결 풀 설정
            pool_size=settings.db_pool_size,          # 기본 연결 수
            max_overflow=settings.db_max_overflow,    # 추가 연결 수
            pool_timeout=settings.db_pool_timeout,    # 연결 대기 시간
            pool_recycle=settings.db_pool_recycle,    # 연결 재사용 시간
            
            # 로깅 및 디버깅
            echo=settings.debug,                      # SQL 쿼리 로깅 (개발 모드만)
            echo_pool=False,                         # 연결 풀 로깅
            
            # 연결 옵션
            pool_pre_ping=True,                      # 연결 유효성 검사
            pool_reset_on_return='commit',           # 반환 시 트랜잭션 정리
            
            # SQLAlchemy 2.0 설정
            future=True
        )
        
        # 비동기 세션 팩토리
        async_session_factory = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,    # 커밋 후에도 객체 접근 가능
            autoflush=True,           # 자동 flush (변경사항 DB 반영)
            autocommit=False          # 수동 커밋 (트랜잭션 제어)
        )
        
        # 동기 엔진 생성 (마이그레이션 등에서 사용)
        sync_engine = create_engine(
            settings.database_sync_url,
            pool_size=10,
            max_overflow=0,
            pool_timeout=30,
            pool_recycle=1800,
            echo=settings.debug,
            pool_pre_ping=True,
            future=True
        )
        
        # 동기 세션 팩토리
        sync_session_factory = sessionmaker(
            bind=sync_engine,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
        
        logger.info("✅ 데이터베이스 엔진 생성 완료")
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 엔진 생성 실패: {e}")
        raise


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션 컨텍스트 매니저
    
    with 구문을 사용하여 안전한 세션 관리를 보장합니다.
    - 자동으로 세션을 시작하고 종료
    - 예외 발생 시 롤백
    - 정상 처리 시 커밋
    
    사용 예:
        async with get_async_session() as session:
            user = User(name="홍길동")
            session.add(user)
            # 자동으로 커밋되고 세션이 닫힘
    """
    if not async_session_factory:
        raise RuntimeError("데이터베이스가 초기화되지 않았습니다. create_database_engines()를 먼저 호출하세요.")
    
    session = async_session_factory()
    try:
        yield session
        await session.commit()  # 성공 시 커밋
    except Exception as e:
        await session.rollback()  # 실패 시 롤백
        logger.error(f"❌ 데이터베이스 세션 오류: {e}")
        raise
    finally:
        await session.close()  # 세션 정리


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 의존성 주입용 세션 생성기
    
    FastAPI의 Depends()에서 사용하는 의존성 함수입니다.
    각 요청마다 새로운 세션을 생성하고 요청 완료 시 자동으로 정리합니다.
    
    사용 예:
        @app.get("/users/{user_id}")
        async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db_session)):
            return await db.get(User, user_id)
    """
    if not async_session_factory:
        raise RuntimeError("데이터베이스가 초기화되지 않았습니다.")
    
    session = async_session_factory()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ DB 세션 오류: {e}")
        raise
    finally:
        await session.close()


def get_sync_session():
    """
    동기 데이터베이스 세션 생성
    
    마이그레이션 스크립트나 동기 작업에서 사용합니다.
    """
    if not sync_session_factory:
        raise RuntimeError("동기 데이터베이스가 초기화되지 않았습니다.")
    
    return sync_session_factory()


async def create_all_tables():
    """
    모든 테이블 생성
    
    애플리케이션 시작 시 필요한 모든 테이블을 생성합니다.
    실제 운영 환경에서는 Alembic 마이그레이션을 사용하는 것이 권장됩니다.
    """
    if not async_engine:
        raise RuntimeError("비동기 엔진이 초기화되지 않았습니다.")
    
    try:
        async with async_engine.begin() as conn:
            # 모든 테이블 생성 (존재하지 않는 경우만)
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ 데이터베이스 테이블 생성 완료")
        
    except Exception as e:
        logger.error(f"❌ 테이블 생성 실패: {e}")
        raise


async def drop_all_tables():
    """
    모든 테이블 삭제
    
    ⚠️ 주의: 모든 데이터가 삭제됩니다!
    테스트 환경에서만 사용하세요.
    """
    if not async_engine:
        raise RuntimeError("비동기 엔진이 초기화되지 않았습니다.")
    
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.warning("⚠️ 모든 테이블이 삭제되었습니다")
        
    except Exception as e:
        logger.error(f"❌ 테이블 삭제 실패: {e}")
        raise


async def check_database_connection() -> bool:
    """
    데이터베이스 연결 상태 확인
    
    헬스체크 엔드포인트에서 사용됩니다.
    
    Returns:
        bool: 연결 성공 시 True, 실패 시 False
    """
    if not async_engine:
        return False
    
    try:
        async with async_engine.begin() as conn:
            # 간단한 쿼리 실행으로 연결 확인
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                logger.debug("✅ 데이터베이스 연결 확인 성공")
                return True
            else:
                logger.warning("⚠️ 데이터베이스 응답이 예상과 다릅니다")
                return False
                
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 확인 실패: {e}")
        return False


async def get_database_info():
    """
    데이터베이스 정보 조회
    
    디버깅이나 모니터링 목적으로 사용됩니다.
    
    Returns:
        dict: 데이터베이스 버전, 설정 정보 등
    """
    if not async_engine:
        return {"error": "데이터베이스가 초기화되지 않았습니다"}
    
    try:
        async with async_engine.begin() as conn:
            # PostgreSQL 버전 확인
            version_result = await conn.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
            # 현재 데이터베이스 이름
            db_name_result = await conn.execute(text("SELECT current_database()"))
            db_name = db_name_result.fetchone()[0]
            
            # 현재 사용자
            user_result = await conn.execute(text("SELECT current_user"))
            current_user = user_result.fetchone()[0]
            
            # 연결 수 확인
            connections_result = await conn.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            )
            active_connections = connections_result.fetchone()[0]
            
            return {
                "version": version,
                "database_name": db_name,
                "current_user": current_user,
                "active_connections": active_connections,
                "engine_pool_size": async_engine.pool.size(),
                "engine_pool_checked_in": async_engine.pool.checkedin(),
                "engine_pool_checked_out": async_engine.pool.checkedout(),
            }
            
    except Exception as e:
        logger.error(f"❌ 데이터베이스 정보 조회 실패: {e}")
        return {"error": str(e)}


async def execute_raw_sql(sql: str, params: dict = None):
    """
    원시 SQL 실행
    
    복잡한 쿼리나 DDL 명령을 실행할 때 사용합니다.
    
    Args:
        sql (str): 실행할 SQL 쿼리
        params (dict): 쿼리 매개변수
        
    Returns:
        결과 데이터 또는 None
    """
    if not async_engine:
        raise RuntimeError("비동기 엔진이 초기화되지 않았습니다.")
    
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text(sql), params or {})
            
            # SELECT 쿼리인 경우 결과 반환
            if sql.strip().upper().startswith('SELECT'):
                return result.fetchall()
            else:
                # INSERT, UPDATE, DELETE 등의 경우 영향받은 행 수 반환
                return result.rowcount
                
    except Exception as e:
        logger.error(f"❌ SQL 실행 실패: {e}")
        raise


async def close_database_connections():
    """
    모든 데이터베이스 연결 종료
    
    애플리케이션 종료 시 호출됩니다.
    """
    global async_engine, sync_engine
    
    try:
        if async_engine:
            await async_engine.dispose()
            logger.info("✅ 비동기 데이터베이스 연결 종료")
        
        if sync_engine:
            sync_engine.dispose()
            logger.info("✅ 동기 데이터베이스 연결 종료")
            
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 종료 중 오류: {e}")


# 유틸리티 클래스
class DatabaseManager:
    """
    데이터베이스 관리를 위한 유틸리티 클래스
    """
    
    @staticmethod
    async def init_database():
        """데이터베이스 초기화"""
        create_database_engines()
        await create_all_tables()
    
    @staticmethod
    async def reset_database():
        """데이터베이스 재설정 (개발/테스트용)"""
        await drop_all_tables()
        await create_all_tables()
    
    @staticmethod
    async def health_check():
        """데이터베이스 헬스체크"""
        is_healthy = await check_database_connection()
        info = await get_database_info()
        
        return {
            "healthy": is_healthy,
            "info": info
        }


# 트랜잭션 데코레이터
def transactional(func):
    """
    트랜잭션을 자동으로 관리하는 데코레이터
    
    함수 실행이 성공하면 커밋하고, 예외가 발생하면 롤백합니다.
    
    사용 예:
        @transactional
        async def create_user_with_profile(user_data, profile_data):
            # 이 함수의 모든 DB 작업이 하나의 트랜잭션으로 처리됩니다
            user = await create_user(user_data)
            profile = await create_profile(profile_data, user.id)
            return user, profile
    """
    async def wrapper(*args, **kwargs):
        async with get_async_session() as session:
            # 첫 번째 인자가 세션이 아니면 세션을 추가
            if args and not isinstance(args[0], AsyncSession):
                result = await func(session, *args, **kwargs)
            else:
                result = await func(*args, **kwargs)
            return result
    
    return wrapper


if __name__ == "__main__":
    """
    데이터베이스 연결 테스트
    """
    async def test_database():
        print("데이터베이스 연결 테스트 시작...")
        
        try:
            # 엔진 생성
            create_database_engines()
            
            # 연결 테스트
            is_connected = await check_database_connection()
            print(f"연결 상태: {'성공' if is_connected else '실패'}")
            
            # 데이터베이스 정보
            info = await get_database_info()
            print(f"데이터베이스 정보: {info}")
            
            # 테이블 생성 테스트
            await create_all_tables()
            print("테이블 생성 완료")
            
        except Exception as e:
            print(f"테스트 실패: {e}")
        finally:
            await close_database_connections()
    
    # 테스트 실행
    asyncio.run(test_database())