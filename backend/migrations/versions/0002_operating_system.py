"""Operational GRC domain records, relationships, approvals and acknowledgements.

Revision ID: 0002
Revises: 0001
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "work_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uid", sa.String(40), nullable=False, unique=True),
        sa.Column("domain", sa.String(30), nullable=False),
        sa.Column("record_type", sa.String(40), nullable=False),
        sa.Column("title_ar", sa.String(240), nullable=False),
        sa.Column("title_en", sa.String(240), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewer_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("approver_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("due_date", sa.String(10)),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("simulated", sa.Boolean, nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
    )
    for column in ("uid", "domain", "record_type", "status", "simulated"):
        op.create_index(f"ix_work_items_{column}", "work_items", [column])
    op.create_table(
        "relationships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_id", sa.Integer, nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.Integer, nullable=False),
        sa.Column("relation", sa.String(50), nullable=False),
        sa.Column("rationale", sa.Text, nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewed_by", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.UniqueConstraint(
            "source_type", "source_id", "target_type", "target_id", "relation",
            name="uq_relationship_edge",
        ),
    )
    for column in ("source_type", "source_id", "target_type", "target_id"):
        op.create_index(f"ix_relationships_{column}", "relationships", [column])
    op.create_table(
        "approvals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("work_item_id", sa.Integer, sa.ForeignKey("work_items.id"), nullable=False),
        sa.Column("step", sa.String(40), nullable=False),
        sa.Column("decision", sa.String(30), nullable=False),
        sa.Column("rationale", sa.Text, nullable=False),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
    )
    op.create_index("ix_approvals_work_item_id", "approvals", ["work_item_id"])
    op.create_table(
        "policy_acknowledgements",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("policy_id", sa.Integer, sa.ForeignKey("work_items.id"), nullable=False),
        sa.Column("subject_ref", sa.String(80), nullable=False),
        sa.Column("subject_name", sa.String(120), nullable=False),
        sa.Column("department", sa.String(80), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("assigned_at", sa.String(40), nullable=False),
        sa.Column("acknowledged_at", sa.String(40)),
        sa.Column("recorded_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("policy_id", "subject_ref", name="uq_policy_subject"),
    )
    op.create_index(
        "ix_policy_acknowledgements_policy_id", "policy_acknowledgements", ["policy_id"]
    )


def downgrade():
    op.drop_table("policy_acknowledgements")
    op.drop_table("approvals")
    op.drop_table("relationships")
    op.drop_table("work_items")
