"""
run_migrations.py - 데이터베이스 마이그레이션 실행 스크립트

이 파일에서 배울 수 있는 개념들:
1. Alembic을 이용한 데이터베이스 마이그레이션
2. 데이터베이스 스키마 버전 관리
3. 프로그래밍 방식의 마이그레이션 실행
4. 에러 핸들링과 롤백
"""

import asyncio
import sys
import os
from alembic.config import Config
from alembic import command
from sqlalchemy import text
import logging

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(__file__))

from database import get_async_engine, DatabaseManager
from config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MigrationManager:
    """
    데이터베이스 마이그레이션을 관리하는 클래스
    """
    
    def __init__(self):
        """Alembic 설정 초기화"""
        self.alembic_cfg = Config("alembic.ini")
        # 데이터베이스 URL 설정
        self.alembic_cfg.set_main_option("sqlalchemy.url", settings.database_sync_url)
        
    async def check_database_connection(self) -> bool:
        """데이터베이스 연결 확인"""
        try:
            engine = get_async_engine()
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ 데이터베이스 연결 확인 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            return False
    
    def run_migration_upgrade(self, revision: str = "head") -> bool:
        """
        마이그레이션 업그레이드 실행
        
        Args:
            revision (str): 업그레이드할 리비전 ("head"는 최신 버전)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"📈 마이그레이션 업그레이드 시작 (리비전: {revision})")
            command.upgrade(self.alembic_cfg, revision)
            logger.info("✅ 마이그레이션 업그레이드 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 마이그레이션 업그레이드 실패: {e}")
            return False
    
    def run_migration_downgrade(self, revision: str) -> bool:
        """
        마이그레이션 다운그레이드 실행
        
        Args:
            revision (str): 다운그레이드할 리비전
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"📉 마이그레이션 다운그레이드 시작 (리비전: {revision})")
            command.downgrade(self.alembic_cfg, revision)
            logger.info("✅ 마이그레이션 다운그레이드 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 마이그레이션 다운그레이드 실패: {e}")
            return False
    
    def show_current_revision(self) -> str:
        """현재 데이터베이스 리비전 조회"""
        try:
            # current 명령은 출력을 반환하지 않으므로 다른 방법 사용
            from alembic.runtime.migration import MigrationContext
            from sqlalchemy import create_engine
            
            engine = create_engine(settings.database_sync_url)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                
            if current_rev:
                logger.info(f"📋 현재 데이터베이스 리비전: {current_rev}")
                return current_rev
            else:
                logger.info("📋 현재 데이터베이스 리비전: 없음 (초기 상태)")
                return "없음"
                
        except Exception as e:
            logger.error(f"❌ 현재 리비전 조회 실패: {e}")
            return "오류"
    
    def show_migration_history(self) -> bool:
        """마이그레이션 히스토리 조회"""
        try:
            logger.info("📚 마이그레이션 히스토리:")
            command.history(self.alembic_cfg)
            return True
        except Exception as e:
            logger.error(f"❌ 마이그레이션 히스토리 조회 실패: {e}")
            return False
    
    def generate_migration(self, message: str, autogenerate: bool = True) -> bool:
        """
        새로운 마이그레이션 파일 생성
        
        Args:
            message (str): 마이그레이션 메시지
            autogenerate (bool): 모델 변경사항을 자동으로 감지할지 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"📝 마이그레이션 파일 생성: {message}")
            command.revision(
                self.alembic_cfg,
                message=message,
                autogenerate=autogenerate
            )
            logger.info("✅ 마이그레이션 파일 생성 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 마이그레이션 파일 생성 실패: {e}")
            return False


async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🗃️ FastAPI Kafka Redis Tutorial - 데이터베이스 마이그레이션")
    print("=" * 60)
    
    migration_manager = MigrationManager()
    
    # 명령행 인자 처리
    if len(sys.argv) < 2:
        print("\n사용법:")
        print("  python run_migrations.py upgrade        # 최신 버전으로 업그레이드")
        print("  python run_migrations.py downgrade 001  # 특정 버전으로 다운그레이드")
        print("  python run_migrations.py current        # 현재 버전 확인")
        print("  python run_migrations.py history        # 마이그레이션 히스토리")
        print("  python run_migrations.py generate 메시지  # 새 마이그레이션 생성")
        print("  python run_migrations.py init           # 데이터베이스 초기화 + 마이그레이션")
        return
    
    command_type = sys.argv[1]
    
    # 데이터베이스 연결 확인 (generate 명령은 제외)
    if command_type != "generate":
        if not await migration_manager.check_database_connection():
            logger.error("데이터베이스 연결을 확인해주세요.")
            return
    
    # 명령 실행
    if command_type == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        migration_manager.run_migration_upgrade(revision)
        
    elif command_type == "downgrade":
        if len(sys.argv) < 3:
            logger.error("다운그레이드할 리비전을 지정해주세요.")
            return
        revision = sys.argv[2]
        migration_manager.run_migration_downgrade(revision)
        
    elif command_type == "current":
        migration_manager.show_current_revision()
        
    elif command_type == "history":
        migration_manager.show_migration_history()
        
    elif command_type == "generate":
        if len(sys.argv) < 3:
            logger.error("마이그레이션 메시지를 지정해주세요.")
            return
        message = " ".join(sys.argv[2:])
        migration_manager.generate_migration(message)
        
    elif command_type == "init":
        # 데이터베이스 초기화 후 마이그레이션 실행
        logger.info("🚀 데이터베이스 전체 초기화 시작")
        
        # 1. 데이터베이스 테이블 생성
        await DatabaseManager.init_database()
        
        # 2. 마이그레이션 업그레이드
        migration_manager.run_migration_upgrade()
        
        # 3. 현재 상태 확인
        migration_manager.show_current_revision()
        
        logger.info("🎉 데이터베이스 초기화 완료!")
        
    else:
        logger.error(f"알 수 없는 명령: {command_type}")
        return
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())