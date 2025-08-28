"""
db_models.py - SQLAlchemy 데이터베이스 모델 정의

이 파일에서 배울 수 있는 개념들:
1. SQLAlchemy 2.0 ORM 모델 작성
2. 테이블 관계 설정 (일대다, 다대다)
3. 인덱스와 제약조건 설정
4. 타임스탬프 자동 관리
5. 데이터베이스 정규화
6. 모델간 관계 매핑
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Float, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint,
    Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
import enum

from database import Base
from models import UserStatus  # Pydantic 모델의 Enum 재사용


class TimestampMixin:
    """
    타임스탬프 관리를 위한 Mixin 클래스
    
    모든 테이블에 공통으로 사용되는 created_at, updated_at 필드를 제공합니다.
    자동으로 현재 시간을 설정하고 업데이트 시에도 자동으로 갱신됩니다.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        comment="수정 시간"
    )


class User(Base, TimestampMixin):
    """
    사용자 테이블
    
    애플리케이션의 핵심 사용자 정보를 저장합니다.
    Pydantic 모델과 구조를 유사하게 유지하되, 
    데이터베이스 특화 기능들을 추가로 제공합니다.
    """
    __tablename__ = "users"
    
    # 기본 키
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="사용자 고유 ID"
    )
    
    # 기본 정보
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="사용자 이름"
    )
    
    email: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True,
        index=True,  # 검색 성능을 위한 인덱스
        comment="이메일 주소"
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="해싱된 비밀번호"
    )
    
    # 선택적 정보
    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="나이"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="전화번호"
    )
    
    # 상태 및 메타데이터
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
        comment="사용자 상태"
    )
    
    login_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="로그인 횟수"
    )
    
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="마지막 로그인 시간"
    )
    
    # JSON 필드 (추가 메타데이터 저장용)
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="추가 메타데이터 (JSON)"
    )
    
    # 관계 설정
    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete-orphan",  # 사용자 삭제 시 관련 아이템도 함께 삭제
        lazy="selectin"  # N+1 문제 방지
    )
    
    user_activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="UserActivity.created_at.desc()",  # 최신순 정렬
        lazy="dynamic"  # 지연 로딩 (필요시에만 조회)
    )
    
    # 제약 조건
    __table_args__ = (
        # 나이 제약 조건
        CheckConstraint('age >= 0 AND age <= 150', name='valid_age_range'),
        
        # 복합 인덱스 (상태별 검색 최적화)
        Index('idx_user_status_email', 'status', 'email'),
        Index('idx_user_created_at', 'created_at'),
        
        # 테이블 코멘트
        {'comment': '사용자 정보 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """모델을 딕셔너리로 변환 (JSON 직렬화용)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'phone': self.phone,
            'status': self.status.value if self.status else None,
            'login_count': self.login_count,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.metadata
        }


class Item(Base, TimestampMixin):
    """
    아이템 테이블
    
    사용자가 소유할 수 있는 아이템들을 저장합니다.
    """
    __tablename__ = "items"
    
    # 기본 키
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="아이템 고유 ID"
    )
    
    # 기본 정보
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="제목"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="설명"
    )
    
    price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="가격"
    )
    
    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,  # 카테고리별 검색을 위한 인덱스
        comment="카테고리"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="활성 상태"
    )
    
    # 외래 키 (사용자와의 관계)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="소유자 ID"
    )
    
    # 관계 설정
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="items"
    )
    
    # 제약 조건
    __table_args__ = (
        # 가격 제약 조건
        CheckConstraint('price >= 0', name='positive_price'),
        
        # 복합 인덱스
        Index('idx_item_owner_category', 'owner_id', 'category'),
        Index('idx_item_active_created', 'is_active', 'created_at'),
        
        # 테이블 코멘트
        {'comment': '아이템 정보 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title='{self.title}', owner_id={self.owner_id})>"


class UserActivity(Base, TimestampMixin):
    """
    사용자 활동 로그 테이블
    
    사용자의 모든 활동을 추적하고 기록합니다.
    감사(Audit) 기능과 사용자 행동 분석에 사용됩니다.
    """
    __tablename__ = "user_activities"
    
    # 기본 키
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="활동 고유 ID"
    )
    
    # 외래 키
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="사용자 ID"
    )
    
    # 활동 정보
    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="활동 타입"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="활동 설명"
    )
    
    # 추가 데이터 (JSON)
    data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="활동 관련 추가 데이터"
    )
    
    # IP 주소 및 사용자 에이전트 (보안/감사용)
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6도 지원하기 위해 45자
        nullable=True,
        comment="IP 주소"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="사용자 에이전트"
    )
    
    # 관계 설정
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_activities"
    )
    
    # 제약 조건
    __table_args__ = (
        # 복합 인덱스 (사용자별 활동 조회 최적화)
        Index('idx_activity_user_type_date', 'user_id', 'activity_type', 'created_at'),
        Index('idx_activity_type_date', 'activity_type', 'created_at'),
        
        # 테이블 코멘트
        {'comment': '사용자 활동 로그 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"


class SystemLog(Base, TimestampMixin):
    """
    시스템 로그 테이블
    
    애플리케이션 시스템 레벨의 이벤트와 로그를 저장합니다.
    """
    __tablename__ = "system_logs"
    
    # 기본 키
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="로그 고유 ID"
    )
    
    # 로그 레벨
    level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="로그 레벨 (INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # 로그 소스
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="로그 소스 (모듈명, 서비스명 등)"
    )
    
    # 로그 메시지
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="로그 메시지"
    )
    
    # 추가 컨텍스트 정보
    context: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="로그 컨텍스트 정보"
    )
    
    # 관련 사용자 (선택적)
    related_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="관련 사용자 ID"
    )
    
    # 제약 조건
    __table_args__ = (
        # 복합 인덱스 (로그 검색 최적화)
        Index('idx_log_level_source_date', 'level', 'source', 'created_at'),
        Index('idx_log_date_level', 'created_at', 'level'),
        
        # 로그 레벨 제약
        CheckConstraint(
            "level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')",
            name='valid_log_level'
        ),
        
        # 테이블 코멘트
        {'comment': '시스템 로그 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<SystemLog(id={self.id}, level='{self.level}', source='{self.source}')>"


class EventLog(Base, TimestampMixin):
    """
    이벤트 로그 테이블
    
    Kafka를 통해 처리된 이벤트들의 기록을 저장합니다.
    이벤트 처리 추적과 재처리에 사용됩니다.
    """
    __tablename__ = "event_logs"
    
    # 기본 키
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="이벤트 로그 ID"
    )
    
    # 이벤트 정보
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="이벤트 타입"
    )
    
    event_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="이벤트 고유 ID (UUID 등)"
    )
    
    # Kafka 관련 정보
    topic: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Kafka 토픽"
    )
    
    partition: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Kafka 파티션"
    )
    
    offset: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Kafka 오프셋"
    )
    
    # 이벤트 데이터
    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="이벤트 페이로드"
    )
    
    # 처리 상태
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="처리 상태"
    )
    
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="처리 완료 시간"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="에러 메시지 (실패한 경우)"
    )
    
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="재시도 횟수"
    )
    
    # 관련 사용자
    related_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="관련 사용자 ID"
    )
    
    # 제약 조건
    __table_args__ = (
        # 복합 인덱스
        Index('idx_event_type_status_date', 'event_type', 'status', 'created_at'),
        Index('idx_event_topic_offset', 'topic', 'partition', 'offset'),
        
        # 상태 제약
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'retrying')",
            name='valid_event_status'
        ),
        
        # 유니크 제약 (중복 처리 방지)
        UniqueConstraint('topic', 'partition', 'offset', name='unique_kafka_message'),
        
        # 테이블 코멘트
        {'comment': '이벤트 처리 로그 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<EventLog(id={self.id}, type='{self.event_type}', status='{self.status}')>"


# 뷰 모델 (읽기 전용)
class UserStatsView(Base):
    """
    사용자 통계 뷰
    
    실제로는 데이터베이스 뷰나 집계 쿼리의 결과를 매핑하는 용도입니다.
    복잡한 통계 데이터를 효율적으로 조회하기 위해 사용합니다.
    """
    __tablename__ = "user_stats_view"
    
    # 가상의 기본 키 (뷰이므로 실제로는 없을 수 있음)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    def __repr__(self) -> str:
        return f"<UserStatsView(user_id={self.user_id}, items={self.total_items})>"


# 데이터베이스 초기화 함수들
def create_indexes():
    """
    추가 인덱스를 생성합니다.
    
    성능 최적화를 위한 커스텀 인덱스들을 정의합니다.
    """
    # 여기에 추가적인 인덱스 생성 코드를 작성할 수 있습니다.
    pass


def create_views():
    """
    데이터베이스 뷰를 생성합니다.
    
    복잡한 집계 쿼리를 뷰로 만들어 성능을 향상시킵니다.
    """
    # 사용자 통계 뷰 생성 예시 (실제 SQL)
    user_stats_view_sql = """
    CREATE OR REPLACE VIEW user_stats_view AS
    SELECT 
        u.id as user_id,
        COUNT(i.id) as total_items,
        COUNT(ua.id) as total_activities,
        MAX(ua.created_at) as last_activity_date
    FROM users u
    LEFT JOIN items i ON u.id = i.owner_id
    LEFT JOIN user_activities ua ON u.id = ua.user_id
    GROUP BY u.id;
    """
    
    # 실제로는 이 SQL을 실행해야 합니다.
    # engine.execute(text(user_stats_view_sql))
    pass


if __name__ == "__main__":
    """
    모델 정보 출력 및 검증
    """
    print("=== SQLAlchemy 모델 정보 ===")
    
    # 모든 테이블 정보 출력
    for table_name, table in Base.metadata.tables.items():
        print(f"\n테이블: {table_name}")
        print(f"  컬럼 수: {len(table.columns)}")
        print(f"  인덱스 수: {len(table.indexes)}")
        print(f"  제약조건 수: {len(table.constraints)}")
        
        # 주요 컬럼 정보
        for column in table.columns:
            nullable = "NULL" if column.nullable else "NOT NULL"
            print(f"    - {column.name}: {column.type} {nullable}")
    
    print(f"\n총 테이블 수: {len(Base.metadata.tables)}")
    
    # 관계 정보 출력
    print("\n=== 테이블 관계 ===")
    for model in [User, Item, UserActivity, EventLog]:
        if hasattr(model, '__mapper__'):
            relationships = model.__mapper__.relationships
            if relationships:
                print(f"{model.__name__}:")
                for rel_name, rel in relationships.items():
                    print(f"  - {rel_name}: {rel.mapper.class_.__name__}")
    
    print("\n모델 검증 완료! 🎉")