"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    업그레이드 마이그레이션
    데이터베이스 스키마를 최신 버전으로 업데이트합니다.
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    다운그레이드 마이그레이션
    이전 버전의 데이터베이스 스키마로 되돌립니다.
    """
    ${downgrades if downgrades else "pass"}