import os
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine,
    Boolean,
    ForeignKey,
    String,
    Text,
    Integer,
    JSON,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def now():
    return datetime.now(timezone.utc).isoformat()


engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./mizan.db"))
if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def sqlite_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")


Session = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    role: Mapped[str] = mapped_column(String(40))
    password: Mapped[str] = mapped_column(Text)


class LoginSession(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires: Mapped[str] = mapped_column(String(40))


class Record(Base):
    """Versioned domain documents; workflow links use relational foreign keys below."""

    __tablename__ = "records"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(240))
    department: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)


class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("records.id"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("records.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(40), default="Not Assessed")
    stage: Mapped[str] = mapped_column(String(30), default="Draft")
    rationale: Mapped[str] = mapped_column(Text, default="")
    period: Mapped[str] = mapped_column(String(30), default="2026-Q4")
    version: Mapped[int] = mapped_column(default=1)


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"))
    filename: Mapped[str] = mapped_column(String(120))
    sha256: Mapped[str] = mapped_column(String(64))
    storage_key: Mapped[str] = mapped_column(String(64))
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created: Mapped[str] = mapped_column(String(40), default=now)
    review_due: Mapped[str] = mapped_column(String(10))


class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"))
    risk_id: Mapped[int] = mapped_column(ForeignKey("records.id"))
    title: Mapped[str] = mapped_column(String(240))
    action: Mapped[str] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    due: Mapped[str] = mapped_column(String(10))
    state: Mapped[str] = mapped_column(String(30), default="Open")


class Activity(Base):
    __tablename__ = "activity"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(80))
    created: Mapped[str] = mapped_column(String(40), default=now)
    details: Mapped[dict] = mapped_column(JSON)
    previous_hash: Mapped[str] = mapped_column(String(64))
    digest: Mapped[str] = mapped_column(String(64))


class WorkItem(Base):
    """Versioned operational record shared by connected GRC domain workflows."""

    __tablename__ = "work_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(30), index=True)
    record_type: Mapped[str] = mapped_column(String(40), index=True)
    title_ar: Mapped[str] = mapped_column(String(240))
    title_en: Mapped[str] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(40), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)
    simulated: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[str] = mapped_column(String(40), default=now)
    updated_at: Mapped[str] = mapped_column(String(40), default=now)


class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint(
            "source_type",
            "source_id",
            "target_type",
            "target_id",
            "relation",
            name="uq_relationship_edge",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(30), index=True)
    source_id: Mapped[int] = mapped_column(Integer, index=True)
    target_type: Mapped[str] = mapped_column(String(30), index=True)
    target_id: Mapped[int] = mapped_column(Integer, index=True)
    relation: Mapped[str] = mapped_column(String(50))
    rationale: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="Approved")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    work_item_id: Mapped[int] = mapped_column(ForeignKey("work_items.id"), index=True)
    step: Mapped[str] = mapped_column(String(40))
    decision: Mapped[str] = mapped_column(String(30))
    rationale: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class PolicyAcknowledgement(Base):
    __tablename__ = "policy_acknowledgements"
    __table_args__ = (
        UniqueConstraint("policy_id", "subject_ref", name="uq_policy_subject"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("work_items.id"), index=True)
    subject_ref: Mapped[str] = mapped_column(String(80))
    subject_name: Mapped[str] = mapped_column(String(120))
    department: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default="Assigned")
    assigned_at: Mapped[str] = mapped_column(String(40), default=now)
    acknowledged_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    recorded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
