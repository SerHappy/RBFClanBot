"""Added statuses

Revision ID: 2c138e3d91e2
Revises: 95c6400ae2ef
Create Date: 2024-03-24 16:56:31.934406

"""

from alembic import op
from typing import Sequence
from typing import Union

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2c138e3d91e2"
down_revision: Union[str, None] = "95c6400ae2ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(
        sa.table("application_statuses", sa.column("status", sa.String(length=266))),
        [
            {"status": "В процессе заполнения"},
            {"status": "Ожидает решения"},
            {"status": "Принята"},
            {"status": "Отклонена"},
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM application_statuses WHERE status IN ('В процессе заполнения', 'Ожидает решения', 'Принята', 'Отклонена')"
    )
