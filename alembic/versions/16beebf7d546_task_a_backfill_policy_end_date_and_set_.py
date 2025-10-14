from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers
revision = "0002_task_a_end_date_not_null"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name
    # Backfill NULL end_date = start_date + 1 year
    if dialect == "sqlite":
        conn.execute(text("""
            UPDATE insurance_policy
            SET end_date = DATE(start_date, '+1 year')
            WHERE end_date IS NULL
        """))
    else:  # e.g., postgresql
        conn.execute(text("""
            UPDATE insurance_policy
            SET end_date = start_date + INTERVAL '1 year'
            WHERE end_date IS NULL
        """))
    # Now set NOT NULL constraint
    with op.batch_alter_table("insurance_policy") as batch_op:
        batch_op.alter_column(
            "end_date",
            existing_type=sa.Date(),
            nullable=False
        )

def downgrade():
    with op.batch_alter_table("insurance_policy") as batch_op:
        batch_op.alter_column(
            "end_date",
            existing_type=sa.Date(),
            nullable=True
        )