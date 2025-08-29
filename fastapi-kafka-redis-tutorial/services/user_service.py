"""
services/user_service.py - PostgreSQL 연동 사용자 비즈니스 로직 서비스 (완전 새 버전)

이 파일에서 배울 수 있는 개념들:
1. SQLAlchemy 2.0 비동기 ORM 사용
2. PostgreSQL과의 실제 데이터베이스 연동
3. 서비스 레이어 패턴 (Business Logic Layer)
4. 트랜잭션 관리와 ACID 특성
5. 캐시-어사이드 패턴 (Cache-Aside Pattern)
6. 이벤트 기반 아키텍처 적용
7. bcrypt를 이용한 안전한 비밀번호 처리
"""
# 타입 힌틴을 위한 기본 타입들 임포트
from typing import List, Optional, Dict, Any
# 날짜 시간처리오 클래스
from datetime import datetime, timedelta
# 로깅 시스템 (디버기, 모니터닐에 필수)
import logging
# 비동기sqlalchemy 세션 postgresql 비동기 연결
from sqlalchemy.ext.asyncio import AsyncSession
# sqlalchemy 쿼리 빌더 함수들 
from sqlalchemy import select, func, and_, or_, update, delete
# 관계형 데이터 로딩
from sqlalchemy.orm import selectinload
# pydantic 모델드 api 입출력 스키마 
from models import User, UserCreate, UserUpdate, UserStatus, EventType
# sqlalchemy orm 모델들(실제 db 테이블 매핑)
from db_models import User as DBUser, UserActivity as DBUserActivity
# 데이터베이스 연결 함수들 
from database import get_async_session, get_async_db_session
# redis 캐싱서비스 
from services.redis_service import redis_service
# kafka 메시징
from services.kafka_service import kafka_service, publish_user_event
# 인증서비스 
from services.auth_service import auth_service


# 로깅 설정
# 로깅 레벨 설정: info 이상 로그만 출력
logging.basicConfig(level=logging.INFO)
# 모듈별로거 생성: 
logger = logging.getLogger(__name__)

# 서비스 클래스 정의 : 비즈니스 로직 담당
class UserService:
    """
    사용자 관련 비즈니스 로직을 처리하는 서비스 클래스
    
    서비스 레이어는 컨트롤러와 데이터 레이어 사이의 비즈니스 로직을 담당합니다.
    - 데이터 검증 및 변환
    - 비즈니스 룰 적용
    - 트랜잭션 관리
    - 캐시 및 이벤트 처리
    - PostgreSQL 데이터베이스 연동
    """
    # 생성자 의존성주입 패턴
    def __init__(self):
        """
        사용자 서비스 초기화
        
        의존성 주입:
        Redis, Kafka, Auth 서비스를 주입받아 사용합니다.
        실제 PostgreSQL 데이터베이스와 연동합니다.
        """
        # redis 서비스 주입 
        self.redis = redis_service
        # kafka  서비스 주입 
        self.kafka = kafka_service
        # auth 서비스 주입
        self.auth = auth_service
        # 초기화 완료 로그 
        logger.info("✅ 사용자 서비스 초기화 완료 (PostgreSQL 연동)")
    
    # 비동기 메서드: 타입 힌팅을 입출력 명시
    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """
        새 사용자 생성
        
        Args:
            user_data (UserCreate): 사용자 생성 데이터
            
        Returns:
            Optional[User]: 생성된 사용자 정보 또는 None
            
        비즈니스 로직:
        1. 이메일 중복 확인 (DB)
        2. 비밀번호 해싱 (bcrypt)
        3. 사용자 정보 저장 (PostgreSQL)
        4. 캐시 저장 (Redis)
        5. 사용자 생성 이벤트 발행 (Kafka)
        6. 활동 로그 기록
        """
        # 트랜잭션 시작/ 컨텍스트 매니져 
        async with get_async_session() as session:
            try:
                # 1. 이메일 중복 확인
                # 중복 체크: 헬퍼 메서드로 이메일 검색
                existing_user = await self._find_user_by_email(session, user_data.email)
                if existing_user:
                    logger.warning(f"⚠️ 이메일 중복: {user_data.email}")
                    return None
                
                # 2. 비밀번호 해싱 (bcrypt 사용)
                hashed_password = self.auth.hash_password(user_data.password)
                
                # 3. 데이터베이스에 사용자 저장
                db_user = DBUser(
                    name=user_data.name,
                    email=user_data.email,
                    password_hash=hashed_password,
                    age=user_data.age,
                    phone=user_data.phone,
                    status=UserStatus.ACTIVE,
                    login_count=0
                )
                
                session.add(db_user)
                await session.flush()  # ID 생성을 위해 flush
                await session.refresh(db_user)  # DB에서 최신 데이터 가져오기
                
                # 4. Pydantic 모델로 변환
                new_user = User(
                    id=db_user.id,
                    name=db_user.name,
                    email=db_user.email,
                    age=db_user.age,
                    phone=db_user.phone,
                    status=db_user.status,
                    login_count=db_user.login_count,
                    created_at=db_user.created_at,
                    updated_at=db_user.updated_at
                )
                
                # 5. 캐시 저장 (Cache-Aside 패턴)
                cache_success = await self.redis.set_user_cache(
                    db_user.id, 
                    new_user.dict(), 
                    expire=3600  # 1시간
                )
                
                if not cache_success:
                    logger.warning(f"⚠️ 사용자 캐시 저장 실패: {db_user.id}")
                
                # 6. 사용자 활동 로그 기록
                await self._log_user_activity(
                    session=session,
                    user_id=db_user.id,
                    activity_type="user_created",
                    description="새 사용자 계정 생성",
                    data={
                        "email": new_user.email,
                        "name": new_user.name
                    }
                )
                
                # 트랜잭션 커밋 (컨텍스트 매니저가 자동 처리)
                
                # 7. 사용자 생성 이벤트 발행 (커밋 후)
                event_success = await publish_user_event(
                    event_type=EventType.USER_CREATED,
                    user_id=db_user.id,
                    data={
                        "email": new_user.email,
                        "name": new_user.name,
                        "created_at": new_user.created_at.isoformat()
                    }
                )
                
                if not event_success:
                    logger.warning(f"⚠️ 사용자 생성 이벤트 발행 실패: {db_user.id}")
                
                logger.info(f"✅ 사용자 생성 성공: {db_user.id} ({new_user.email})")
                return new_user
                
            except Exception as e:
                logger.error(f"❌ 사용자 생성 중 오류: {e}")
                return None
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        사용자 정보 조회
        
        Cache-Aside 패턴 적용:
        1. 캐시에서 먼저 조회 (Redis)
        2. 캐시 미스 시 DB에서 조회 (PostgreSQL)
        3. DB 결과를 캐시에 저장
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Optional[User]: 사용자 정보 또는 None
        """
        try:
            # 1. 캐시에서 먼저 조회
            cached_user = await self.redis.get_user_cache(user_id)
            if cached_user:
                logger.info(f"🎯 캐시 히트: 사용자 {user_id}")
                return User(**cached_user)
            
            # 2. 캐시 미스 - PostgreSQL에서 조회
            logger.info(f"🔍 캐시 미스: 사용자 {user_id} - DB 조회")
            
            async with get_async_session() as session:
                # SQLAlchemy 조회 쿼리
                stmt = select(DBUser).where(DBUser.id == user_id)
                result = await session.execute(stmt)
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    logger.info(f"🚫 사용자 없음: {user_id}")
                    return None
                
                # 3. Pydantic 모델로 변환
                user = User(
                    id=db_user.id,
                    name=db_user.name,
                    email=db_user.email,
                    age=db_user.age,
                    phone=db_user.phone,
                    status=db_user.status,
                    login_count=db_user.login_count,
                    created_at=db_user.created_at,
                    updated_at=db_user.updated_at
                )
                
                # 4. 캐시에 저장 (다음번 조회 시 빠른 응답)
                await self.redis.set_user_cache(user_id, user.dict(), expire=3600)
                
                logger.info(f"✅ 사용자 조회 성공: {user_id}")
                return user
            
        except Exception as e:
            logger.error(f"❌ 사용자 조회 중 오류 ({user_id}): {e}")
            return None
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        사용자 정보 수정
        
        Args:
            user_id (int): 사용자 ID
            user_update (UserUpdate): 수정할 정보
            
        Returns:
            Optional[User]: 수정된 사용자 정보 또는 None
        """
        async with get_async_session() as session:
            try:
                # 1. 사용자 존재 확인
                stmt = select(DBUser).where(DBUser.id == user_id)
                result = await session.execute(stmt)
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    logger.warning(f"⚠️ 수정할 사용자 없음: {user_id}")
                    return None
                
                # 2. 수정할 데이터 준비 (None이 아닌 값만 업데이트)
                update_data = user_update.dict(exclude_unset=True)
                changed_fields = []
                
                for field, value in update_data.items():
                    if hasattr(db_user, field) and getattr(db_user, field) != value:
                        setattr(db_user, field, value)
                        changed_fields.append(field)
                
                # 수정된 내용이 없으면 현재 사용자 정보 반환
                if not changed_fields:
                    logger.info(f"ℹ️ 수정할 내용 없음: {user_id}")
                    return User(
                        id=db_user.id,
                        name=db_user.name,
                        email=db_user.email,
                        age=db_user.age,
                        phone=db_user.phone,
                        status=db_user.status,
                        login_count=db_user.login_count,
                        created_at=db_user.created_at,
                        updated_at=db_user.updated_at
                    )
                
                # 3. 수정 시간 업데이트 (자동으로 처리됨)
                db_user.updated_at = datetime.now()
                
                await session.flush()
                await session.refresh(db_user)
                
                # 4. 수정된 User 모델 생성
                updated_user = User(
                    id=db_user.id,
                    name=db_user.name,
                    email=db_user.email,
                    age=db_user.age,
                    phone=db_user.phone,
                    status=db_user.status,
                    login_count=db_user.login_count,
                    created_at=db_user.created_at,
                    updated_at=db_user.updated_at
                )
                
                # 5. 캐시 무효화 (데이터 일관성 유지)
                cache_deleted = await self.redis.delete_user_cache(user_id)
                if cache_deleted:
                    logger.info(f"🗑️ 사용자 캐시 삭제: {user_id}")
                
                # 6. 활동 로그 기록
                await self._log_user_activity(
                    session=session,
                    user_id=user_id,
                    activity_type="user_updated",
                    description=f"사용자 정보 수정: {', '.join(changed_fields)}",
                    data={"changed_fields": changed_fields}
                )
                
                # 7. 사용자 수정 이벤트 발행
                event_success = await publish_user_event(
                    event_type=EventType.USER_UPDATED,
                    user_id=user_id,
                    data={
                        "changed_fields": changed_fields,
                        "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
                    }
                )
                
                if not event_success:
                    logger.warning(f"⚠️ 사용자 수정 이벤트 발행 실패: {user_id}")
                
                logger.info(f"✅ 사용자 수정 성공: {user_id} (변경: {changed_fields})")
                return updated_user
                
            except Exception as e:
                logger.error(f"❌ 사용자 수정 중 오류 ({user_id}): {e}")
                return None
    
    async def delete_user(self, user_id: int) -> bool:
        """
        사용자 삭제 (소프트 삭제)
        
        실제로는 데이터를 삭제하지 않고 상태를 변경합니다.
        
        Args:
            user_id (int): 삭제할 사용자 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        async with get_async_session() as session:
            try:
                # 1. 사용자 존재 확인
                stmt = select(DBUser).where(DBUser.id == user_id)
                result = await session.execute(stmt)
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    logger.warning(f"⚠️ 삭제할 사용자 없음: {user_id}")
                    return False
                
                # 2. 소프트 삭제 (상태 변경)
                db_user.status = UserStatus.INACTIVE
                db_user.updated_at = datetime.now()
                
                await session.flush()
                
                # 3. 캐시에서 삭제
                await self.redis.delete_user_cache(user_id)
                
                # 4. 활동 로그 기록
                await self._log_user_activity(
                    session=session,
                    user_id=user_id,
                    activity_type="user_deleted",
                    description="사용자 계정 삭제 (소프트 삭제)",
                    data={"soft_delete": True}
                )
                
                # 5. 사용자 삭제 이벤트 발행
                await publish_user_event(
                    event_type=EventType.USER_DELETED,
                    user_id=user_id,
                    data={
                        "deleted_at": datetime.now().isoformat(),
                        "soft_delete": True
                    }
                )
                
                logger.info(f"✅ 사용자 삭제 성공: {user_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ 사용자 삭제 중 오류 ({user_id}): {e}")
                return False
    
    async def list_users(self, skip: int = 0, limit: int = 100, status: Optional[UserStatus] = None) -> List[User]:
        """
        사용자 목록 조회 (페이징 지원)
        
        Args:
            skip (int): 건너뛸 개수
            limit (int): 최대 조회 개수
            status (Optional[UserStatus]): 필터링할 상태
            
        Returns:
            List[User]: 사용자 목록
        """
        async with get_async_session() as session:
            try:
                # 1. 기본 쿼리 생성
                stmt = select(DBUser)
                
                # 2. 상태 필터링
                if status:
                    stmt = stmt.where(DBUser.status == status)
                
                # 3. 정렬 (최신순)
                stmt = stmt.order_by(DBUser.created_at.desc())
                
                # 4. 페이징
                stmt = stmt.offset(skip).limit(limit)
                
                # 5. 쿼리 실행
                result = await session.execute(stmt)
                db_users = result.scalars().all()
                
                # 6. Pydantic 모델로 변환
                users = [
                    User(
                        id=db_user.id,
                        name=db_user.name,
                        email=db_user.email,
                        age=db_user.age,
                        phone=db_user.phone,
                        status=db_user.status,
                        login_count=db_user.login_count,
                        created_at=db_user.created_at,
                        updated_at=db_user.updated_at
                    )
                    for db_user in db_users
                ]
                
                logger.info(f"✅ 사용자 목록 조회: {len(users)}명 (스킵: {skip}, 제한: {limit})")
                return users
                
            except Exception as e:
                logger.error(f"❌ 사용자 목록 조회 중 오류: {e}")
                return []
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        사용자 인증
        
        Args:
            email (str): 이메일
            password (str): 비밀번호
            
        Returns:
            Optional[User]: 인증된 사용자 정보 또는 None
        """
        async with get_async_session() as session:
            try:
                # 1. 이메일로 사용자 찾기
                db_user = await self._find_user_by_email(session, email)
                if not db_user:
                    logger.warning(f"⚠️ 존재하지 않는 사용자: {email}")
                    return None
                
                # 2. 비밀번호 검증 (bcrypt)
                if not self.auth.verify_password(password, db_user.password_hash):
                    logger.warning(f"⚠️ 비밀번호 불일치: {email}")
                    return None
                
                # 3. 비활성 사용자 체크
                if db_user.status != UserStatus.ACTIVE:
                    logger.warning(f"⚠️ 비활성 사용자: {email}")
                    return None
                
                # 4. 로그인 횟수 증가
                db_user.login_count += 1
                db_user.last_login_at = datetime.now()
                db_user.updated_at = datetime.now()
                
                await session.flush()
                await session.refresh(db_user)
                
                # 5. 캐시 무효화 (로그인 횟수 변경으로 인해)
                await self.redis.delete_user_cache(db_user.id)
                
                # 6. 활동 로그 기록
                await self._log_user_activity(
                    session=session,
                    user_id=db_user.id,
                    activity_type="user_login",
                    description="사용자 로그인",
                    data={"email": email, "login_count": db_user.login_count}
                )
                
                # 7. User 모델 반환 (비밀번호 제외)
                user = User(
                    id=db_user.id,
                    name=db_user.name,
                    email=db_user.email,
                    age=db_user.age,
                    phone=db_user.phone,
                    status=db_user.status,
                    login_count=db_user.login_count,
                    created_at=db_user.created_at,
                    updated_at=db_user.updated_at
                )
                
                # 8. 로그인 이벤트 발행
                await publish_user_event(
                    event_type=EventType.USER_LOGIN,
                    user_id=db_user.id,
                    data={
                        "email": email,
                        "login_at": db_user.last_login_at.isoformat() if db_user.last_login_at else None,
                        "login_count": db_user.login_count
                    }
                )
                
                logger.info(f"✅ 사용자 인증 성공: {email}")
                return user
                
            except Exception as e:
                logger.error(f"❌ 사용자 인증 중 오류 ({email}): {e}")
                return None
    
    async def get_user_stats(self) -> Dict[str, int]:
        """
        사용자 통계 정보 조회
        
        Returns:
            Dict[str, int]: 통계 정보
        """
        async with get_async_session() as session:
            try:
                # 전체 사용자 수
                total_stmt = select(func.count(DBUser.id))
                total_result = await session.execute(total_stmt)
                total_users = total_result.scalar()
                
                # 활성 사용자 수
                active_stmt = select(func.count(DBUser.id)).where(DBUser.status == UserStatus.ACTIVE)
                active_result = await session.execute(active_stmt)
                active_users = active_result.scalar()
                
                # 오늘 가입한 사용자 수
                today = datetime.now().date()
                today_stmt = select(func.count(DBUser.id)).where(func.date(DBUser.created_at) == today)
                today_result = await session.execute(today_stmt)
                new_users_today = today_result.scalar()
                
                stats = {
                    "total_users": total_users or 0,
                    "active_users": active_users or 0,
                    "inactive_users": (total_users or 0) - (active_users or 0),
                    "new_users_today": new_users_today or 0
                }
                
                logger.info(f"📊 사용자 통계: {stats}")
                return stats
                
            except Exception as e:
                logger.error(f"❌ 사용자 통계 조회 중 오류: {e}")
                return {}
    
    # 내부 헬퍼 메서드들
    async def _find_user_by_email(self, session: AsyncSession, email: str) -> Optional[DBUser]:
        """
        이메일로 사용자 검색 (PostgreSQL)
        
        데이터베이스 인덱스를 사용하여 빠른 검색이 가능합니다.
        이메일 필드에 UNIQUE 인덱스가 설정되어 있습니다.
        
        Args:
            session (AsyncSession): 데이터베이스 세션
            email (str): 검색할 이메일 주소
            
        Returns:
            Optional[DBUser]: 찾은 사용자 또는 None
        """
        try:
            stmt = select(DBUser).where(func.lower(DBUser.email) == func.lower(email))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ 이메일로 사용자 검색 중 오류: {e}")
            return None
    
    async def _log_user_activity(
        self, 
        session: AsyncSession,
        user_id: int, 
        activity_type: str, 
        description: str = None,
        data: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> bool:
        """
        사용자 활동 로그 기록 (PostgreSQL)
        
        Args:
            session (AsyncSession): 데이터베이스 세션
            user_id (int): 사용자 ID
            activity_type (str): 활동 타입
            description (str): 활동 설명
            data (Dict[str, Any]): 추가 데이터
            ip_address (str): IP 주소
            user_agent (str): 사용자 에이전트
            
        Returns:
            bool: 성공 여부
        """
        try:
            activity_log = DBUserActivity(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                data=data or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            session.add(activity_log)
            # 세션이 자동으로 커밋될 것이므로 여기서는 flush만
            await session.flush()
            
            logger.debug(f"📝 사용자 활동 로그 기록: {user_id} - {activity_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 사용자 활동 로그 기록 중 오류: {e}")
            return False


# 싱글톤 인스턴스 생성
user_service = UserService()


if __name__ == "__main__":
    """
    사용자 서비스 테스트 코드
    """
    import asyncio
    from database import DatabaseManager
    
    async def test_user_service():
        print("사용자 서비스 테스트 시작...")
        
        # 데이터베이스 초기화
        await DatabaseManager.init_database()
        
        # 사용자 생성 테스트
        user_data = UserCreate(
            name="홍길동",
            email="hong@example.com",
            password="password123",
            age=25,
            phone="01012345678"
        )
        
        new_user = await user_service.create_user(user_data)
        if new_user:
            print(f"✅ 사용자 생성: {new_user.name} ({new_user.id})")
            
            # 사용자 조회 테스트
            user = await user_service.get_user(new_user.id)
            print(f"✅ 사용자 조회: {user.name if user else 'None'}")
            
            # 사용자 인증 테스트
            auth_user = await user_service.authenticate_user(
                "hong@example.com", "password123"
            )
            print(f"✅ 사용자 인증: {auth_user.name if auth_user else 'None'}")
            
            # 통계 조회 테스트
            stats = await user_service.get_user_stats()
            print(f"📊 사용자 통계: {stats}")
    
    # 테스트 실행
    asyncio.run(test_user_service())