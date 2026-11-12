"""Initial single-organization relational workflow schema.

Revision ID: 0001
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("role", sa.String(40), nullable=False),
        sa.Column("password", sa.Text, nullable=False),
    )
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires", sa.String(40), nullable=False),
    )
    op.create_table(
        "records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("department", sa.String(80), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
    )
    op.create_index("ix_records_kind", "records", ["kind"])
    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "control_id", sa.Integer, sa.ForeignKey("records.id"), nullable=False
        ),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("records.id"), nullable=False),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewer_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("stage", sa.String(30), nullable=False),
        sa.Column("rationale", sa.Text, nullable=False),
        sa.Column("period", sa.String(30), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
    )
    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "assessment_id", sa.Integer, sa.ForeignKey("assessments.id"), nullable=False
        ),
        sa.Column("filename", sa.String(120), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("storage_key", sa.String(64), nullable=False),
        sa.Column("uploaded_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created", sa.String(40), nullable=False),
        sa.Column("review_due", sa.String(10), nullable=False),
    )
    op.create_table(
        "findings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "assessment_id", sa.Integer, sa.ForeignKey("assessments.id"), nullable=False
        ),
        sa.Column("risk_id", sa.Integer, sa.ForeignKey("records.id"), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("due", sa.String(10), nullable=False),
        sa.Column("state", sa.String(30), nullable=False),
    )
    op.create_table(
        "activity",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor", sa.String(80), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("target", sa.String(80), nullable=False),
        sa.Column("created", sa.String(40), nullable=False),
        sa.Column("details", sa.JSON, nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=False),
        sa.Column("digest", sa.String(64), nullable=False),
    )


def downgrade():
    for name in [
        "activity",
        "findings",
        "evidence",
        "assessments",
        "records",
        "sessions",
        "users",
    ]:
        op.drop_table(name)
