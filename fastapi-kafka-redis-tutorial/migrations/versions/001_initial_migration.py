"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

이 마이그레이션에서 생성되는 테이블들:
1. users - 사용자 정보
2. user_activities - 사용자 활동 로그
3. items - 아이템 정보
4. system_logs - 시스템 로그
5. event_logs - 이벤트 로그
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    초기 데이터베이스 스키마 생성
    """
    
    # users 테이블 생성
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='사용자 이름'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='이메일 주소'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='해시된 비밀번호'),
        sa.Column('age', sa.Integer(), nullable=True, comment='나이'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='전화번호'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='사용자 상태'),
        sa.Column('login_count', sa.Integer(), server_default='0', nullable=False, comment='로그인 횟수'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True, comment='마지막 로그인 시간'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='생성 시간'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='수정 시간'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        comment='사용자 정보 테이블'
    )
    
    # users 테이블 인덱스 생성
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_status', 'users', ['status'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    
    # user_activities 테이블 생성
    op.create_table(
        'user_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='사용자 ID'),
        sa.Column('activity_type', sa.String(length=100), nullable=False, comment='활동 유형'),
        sa.Column('description', sa.Text(), nullable=True, comment='활동 설명'),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='추가 데이터'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP 주소'),
        sa.Column('user_agent', sa.Text(), nullable=True, comment='사용자 에이전트'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='생성 시간'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='사용자 활동 로그 테이블'
    )
    
    # user_activities 테이블 인덱스 생성
    op.create_index('ix_user_activities_user_id', 'user_activities', ['user_id'])
    op.create_index('ix_user_activities_activity_type', 'user_activities', ['activity_type'])
    op.create_index('ix_user_activities_created_at', 'user_activities', ['created_at'])
    
    # items 테이블 생성
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, comment='아이템 이름'),
        sa.Column('description', sa.Text(), nullable=True, comment='아이템 설명'),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False, comment='가격'),
        sa.Column('category', sa.String(length=100), nullable=True, comment='카테고리'),
        sa.Column('is_available', sa.Boolean(), server_default='true', nullable=False, comment='판매 가능 여부'),
        sa.Column('stock_quantity', sa.Integer(), server_default='0', nullable=False, comment='재고 수량'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='메타데이터'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='생성 시간'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='수정 시간'),
        sa.PrimaryKeyConstraint('id'),
        comment='아이템 정보 테이블'
    )
    
    # items 테이블 인덱스 생성
    op.create_index('ix_items_category', 'items', ['category'])
    op.create_index('ix_items_is_available', 'items', ['is_available'])
    op.create_index('ix_items_price', 'items', ['price'])
    op.create_index('ix_items_created_at', 'items', ['created_at'])
    
    # system_logs 테이블 생성
    op.create_table(
        'system_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False, comment='로그 레벨'),
        sa.Column('message', sa.Text(), nullable=False, comment='로그 메시지'),
        sa.Column('component', sa.String(length=100), nullable=True, comment='컴포넌트명'),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='추가 데이터'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='생성 시간'),
        sa.PrimaryKeyConstraint('id'),
        comment='시스템 로그 테이블'
    )
    
    # system_logs 테이블 인덱스 생성
    op.create_index('ix_system_logs_level', 'system_logs', ['level'])
    op.create_index('ix_system_logs_component', 'system_logs', ['component'])
    op.create_index('ix_system_logs_created_at', 'system_logs', ['created_at'])
    
    # event_logs 테이블 생성
    op.create_table(
        'event_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False, comment='이벤트 타입'),
        sa.Column('entity_type', sa.String(length=100), nullable=True, comment='엔티티 타입'),
        sa.Column('entity_id', sa.Integer(), nullable=True, comment='엔티티 ID'),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='이벤트 데이터'),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='사용자 ID'),
        sa.Column('session_id', sa.String(length=255), nullable=True, comment='세션 ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='생성 시간'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='이벤트 로그 테이블'
    )
    
    # event_logs 테이블 인덱스 생성
    op.create_index('ix_event_logs_event_type', 'event_logs', ['event_type'])
    op.create_index('ix_event_logs_entity_type', 'event_logs', ['entity_type'])
    op.create_index('ix_event_logs_entity_id', 'event_logs', ['entity_id'])
    op.create_index('ix_event_logs_user_id', 'event_logs', ['user_id'])
    op.create_index('ix_event_logs_created_at', 'event_logs', ['created_at'])
    
    print("✅ 초기 데이터베이스 스키마 생성 완료")


def downgrade() -> None:
    """
    초기 스키마 제거 (모든 테이블 삭제)
    """
    
    # 외래 키 때문에 역순으로 삭제
    op.drop_table('event_logs')
    op.drop_table('system_logs')
    op.drop_table('items')
    op.drop_table('user_activities')
    op.drop_table('users')
    
    print("✅ 초기 데이터베이스 스키마 제거 완료")