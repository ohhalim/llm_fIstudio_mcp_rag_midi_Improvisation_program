"""
Alembic 환경 설정 파일

이 파일에서 배울 수 있는 개념들:
1. Alembic 환경 설정
2. 비동기 데이터베이스 연결
3. SQLAlchemy 메타데이터 설정
4. 마이그레이션 자동 생성
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
import os
import sys

# FastAPI 프로젝트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# config 객체는 alembic.ini 파일의 값들에 대한 접근을 제공
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모델의 MetaData 객체를 가져와서 'autogenerate' 지원을 위해 추가
from db_models import Base
from config import settings

target_metadata = Base.metadata

# 데이터베이스 URL을 설정에서 가져옴
config.set_main_option("sqlalchemy.url", settings.database_sync_url)


def run_migrations_offline() -> None:
    """
    오프라인 모드에서 마이그레이션 실행
    
    이 모드에서는 Engine이나 Connection을 생성하지 않고
    데이터베이스 URL만을 사용하여 SQL을 생성합니다.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    실제 마이그레이션을 실행하는 함수
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    온라인 모드에서 마이그레이션 실행
    
    이 모드에서는 실제 데이터베이스 연결을 생성합니다.
    """
    # 동기 엔진 설정 (Alembic은 동기 엔진이 필요함)
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_sync_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())