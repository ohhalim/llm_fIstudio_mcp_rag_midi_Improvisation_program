from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import DatabaseSettings

Base = declarative_base()

class DatabaseManager:
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
    
    def init_sync_db(self):
        """동기 데이터베이스 초기화"""
        self.engine = create_engine(
            self.settings.database_url,
            echo=self.settings.echo
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def init_async_db(self):
        """비동기 데이터베이스 초기화"""
        async_url = self.settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        self.async_engine = create_async_engine(
            async_url,
            echo=self.settings.echo
        )
        self.AsyncSessionLocal = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    def get_sync_session(self):
        """동기 세션 의존성"""
        if not self.SessionLocal:
            self.init_sync_db()
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    async def get_async_session(self):
        """비동기 세션 의존성"""
        if not self.AsyncSessionLocal:
            self.init_async_db()
        
        async with self.AsyncSessionLocal() as session:
            yield session
    
    async def create_tables(self):
        """테이블 생성"""
        if not self.async_engine:
            self.init_async_db()
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# 글로벌 데이터베이스 매니저 인스턴스
db_manager = None

def init_database(settings: DatabaseSettings):
    global db_manager
    db_manager = DatabaseManager(settings)
    return db_manager

def get_db():
    """FastAPI 의존성으로 사용할 데이터베이스 세션"""
    return db_manager.get_sync_session()

async def get_async_db():
    """FastAPI 의존성으로 사용할 비동기 데이터베이스 세션"""
    async for session in db_manager.get_async_session():
        yield session