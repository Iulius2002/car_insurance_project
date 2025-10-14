from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "owner",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
    )
    op.create_table(
        "car",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vin", sa.String(length=32), nullable=False, unique=True),
        sa.Column("make", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("year_of_manufacture", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("owner.id", ondelete="RESTRICT"), nullable=False),
    )
    op.create_table(
        "insurance_policy",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("car.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        # For demonstration of Task A, start as NULL-able in baseline:
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("logged_expiry_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_policy_car_dates", "insurance_policy", ["car_id", "start_date", "end_date"])
    op.create_table(
        "claim",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("car.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_claim_car_date", "claim", ["car_id", "claim_date"])

def downgrade():
    op.drop_index("ix_claim_car_date", table_name="claim")
    op.drop_table("claim")
    op.drop_index("ix_policy_car_dates", table_name="insurance_policy")
    op.drop_table("insurance_policy")
    op.drop_table("car")
    op.drop_table("owner")