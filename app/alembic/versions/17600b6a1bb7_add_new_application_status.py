"""Add new application status

Revision ID: 17600b6a1bb7
Revises: 00d4ae939070
Create Date: 2024-04-06 17:17:27.183144

"""

from alembic import op
from typing import Sequence
from typing import Union

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "17600b6a1bb7"
down_revision: Union[str, None] = "00d4ae939070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO application_statuses (id, status) VALUES (5, 'В обработке');")


def downgrade() -> None:
    op.execute("DELETE FROM application_statuses WHERE status = 'В обработке';")
