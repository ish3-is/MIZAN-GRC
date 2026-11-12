from datetime import date
from typing import Literal

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, or_, select

from .core import app, db, actor, activity, encode, fetch, permit
from .db import (
    Approval,
    PolicyAcknowledgement,
    Relationship,
    User,
    WorkItem,
    now,
)

DOMAINS = {
    "governance",
    "policy",
    "privacy",
    "vendor",
    "incident",
    "continuity",
    "training",
    "audit",
    "evidence",
    "gap",
    "remediation",
}
EDIT_ROLES = {"Super Admin", "GRC Manager", "GRC Analyst", "Compliance Officer", "Privacy Officer"}
VERIFY_ROLES = {"Super Admin", "GRC Manager", "Internal Auditor"}

LIFECYCLES = {
    "policy": {
        "Draft": {"Under Review"},
        "Under Review": {"Draft", "Approved"},
        "Approved": {"Published", "Draft"},
        "Published": {"Expired", "Retired", "Draft"},
        "Expired": {"Draft", "Retired"},
        "Retired": set(),
    },
    "default": {
        "Draft": {"Under Review", "Open"},
        "Open": {"Planned", "In Progress", "Deferred", "Rejected"},
        "Planned": {"In Progress", "Deferred", "Rejected"},
        "Under Review": {"Draft", "Approved", "In Progress"},
        "Approved": {"In Progress", "Closed"},
        "In Progress": {"Pending Verification", "Deferred"},
        "Pending Verification": {"In Progress", "Closed"},
        "Deferred": {"Open", "In Progress"},
        "Rejected": {"Open"},
        "Closed": {"Open"},
    },
}


def work_item_view(item: WorkItem, s):
    value = encode(item)
    value["owner"] = s.get(User, item.owner_id).username
    value["reviewer"] = s.get(User, item.reviewer_id).username if item.reviewer_id else None
    value["approver"] = s.get(User, item.approver_id).username if item.approver_id else None
    value["simulation_label"] = (
        "SIMULATED DATA — NOT REAL ORGANIZATIONAL EVIDENCE" if item.simulated else None
    )
    value["approvals"] = [
        encode(a)
        for a in s.scalars(
            select(Approval).where(Approval.work_item_id == item.id).order_by(Approval.id)
        )
    ]
    return value


@app.get("/api/work-items")
def work_items(
    domain: str | None = None,
    status: str | None = None,
    q: str | None = Query(default=None, max_length=100),
    user=Depends(actor),
    s=Depends(db),
):
    query = select(WorkItem).order_by(WorkItem.domain, WorkItem.uid)
    if domain:
        if domain not in DOMAINS:
            raise HTTPException(422, "Unknown GRC domain")
        query = query.where(WorkItem.domain == domain)
    if status:
        query = query.where(WorkItem.status == status)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                WorkItem.uid.ilike(pattern),
                WorkItem.title_ar.ilike(pattern),
                WorkItem.title_en.ilike(pattern),
            )
        )
    return [work_item_view(item, s) for item in s.scalars(query)]


@app.get("/api/work-items/{id}")
def work_item(id: int, user=Depends(actor), s=Depends(db)):
    return work_item_view(fetch(s, WorkItem, id), s)


class WorkItemInput(BaseModel):
    domain: str
    record_type: str = Field(min_length=2, max_length=40)
    title_ar: str = Field(min_length=3, max_length=240)
    title_en: str = Field(min_length=3, max_length=240)
    status: str = "Draft"
    owner_id: int
    reviewer_id: int | None = None
    approver_id: int | None = None
    due_date: str | None = None
    payload: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_assignment(self):
        if self.domain not in DOMAINS:
            raise ValueError("Unknown GRC domain")
        if self.approver_id and self.approver_id == self.owner_id:
            raise ValueError("Owner cannot approve their own record")
        if self.reviewer_id and self.reviewer_id == self.owner_id:
            raise ValueError("Owner cannot independently review their own record")
        return self


def next_uid(s, domain):
    prefix = {
        "governance": "GOV",
        "policy": "POL",
        "privacy": "PRV",
        "vendor": "VEN",
        "incident": "INC",
        "continuity": "BCM",
        "training": "TRN",
        "audit": "AUD",
        "evidence": "EVD",
        "gap": "GAP",
        "remediation": "REM",
    }[domain]
    count = s.scalar(select(func.count(WorkItem.id)).where(WorkItem.domain == domain))
    return f"NAM-{prefix}-{count + 1:03}"


@app.post("/api/work-items", status_code=201)
def create_work_item(data: WorkItemInput, user=Depends(actor), s=Depends(db)):
    permit(user, EDIT_ROLES)
    for id in {data.owner_id, data.reviewer_id, data.approver_id} - {None}:
        fetch(s, User, id)
    item = WorkItem(
        uid=next_uid(s, data.domain),
        **data.model_dump(),
        simulated=True,
        created_by=user.id,
        updated_by=user.id,
        created_at=now(),
        updated_at=now(),
    )
    s.add(item)
    s.flush()
    activity(s, user, f"{data.domain}.created", item.uid, {"status": item.status})
    s.commit()
    return work_item_view(item, s)


class WorkItemUpdate(BaseModel):
    title_ar: str = Field(min_length=3, max_length=240)
    title_en: str = Field(min_length=3, max_length=240)
    owner_id: int
    reviewer_id: int | None = None
    approver_id: int | None = None
    due_date: str | None = None
    payload: dict
    version: int

    @model_validator(mode="after")
    def separation(self):
        if self.owner_id in {self.reviewer_id, self.approver_id}:
            raise ValueError("Owner, reviewer and approver must be separated")
        return self


@app.put("/api/work-items/{id}")
def update_work_item(id: int, data: WorkItemUpdate, user=Depends(actor), s=Depends(db)):
    item = fetch(s, WorkItem, id)
    if user.id != item.owner_id and user.role not in EDIT_ROLES:
        raise HTTPException(403, "Only the owner or GRC team may update this record")
    if item.version != data.version:
        raise HTTPException(409, "Record changed; reload before saving")
    for user_id in {data.owner_id, data.reviewer_id, data.approver_id} - {None}:
        fetch(s, User, user_id)
    before = item.version
    for key, value in data.model_dump(exclude={"version"}).items():
        setattr(item, key, value)
    item.version += 1
    item.updated_by = user.id
    item.updated_at = now()
    activity(s, user, f"{item.domain}.updated", item.uid, {"from_version": before, "to_version": item.version})
    s.commit()
    return work_item_view(item, s)


class Transition(BaseModel):
    status: str = Field(min_length=3, max_length=40)
    rationale: str = Field(min_length=12, max_length=1000)


@app.post("/api/work-items/{id}/transition")
def transition_work_item(id: int, data: Transition, user=Depends(actor), s=Depends(db)):
    item = fetch(s, WorkItem, id)
    lifecycle = LIFECYCLES.get(item.domain, LIFECYCLES["default"])
    if data.status not in lifecycle.get(item.status, set()):
        raise HTTPException(409, f"Invalid transition from {item.status} to {data.status}")
    approval_states = {"Approved", "Published", "Closed"}
    if data.status in approval_states:
        permit(user, VERIFY_ROLES)
        if user.id in {item.owner_id, item.reviewer_id}:
            raise HTTPException(403, "Independent approval cannot be performed by the owner or reviewer")
        if item.approver_id and user.id != item.approver_id and user.role != "Super Admin":
            raise HTTPException(403, "Record is assigned to a different approver")
        if item.domain in {"gap", "remediation"} and data.status == "Closed":
            if not item.payload.get("completion_evidence_ids") or not item.payload.get("verification_result"):
                raise HTTPException(409, "Closure requires completion evidence and a verification result")
    elif user.id != item.owner_id and user.role not in EDIT_ROLES | VERIFY_ROLES:
        raise HTTPException(403, "Role cannot move this record")
    previous = item.status
    item.status = data.status
    item.version += 1
    item.updated_by = user.id
    item.updated_at = now()
    s.add(
        Approval(
            work_item_id=item.id,
            step=f"{previous} → {data.status}",
            decision=data.status,
            rationale=data.rationale,
            actor_id=user.id,
        )
    )
    activity(s, user, f"{item.domain}.transitioned", item.uid, {"from": previous, "to": data.status})
    s.commit()
    return work_item_view(item, s)


class RelationshipInput(BaseModel):
    source_type: Literal["record", "work_item", "assessment", "evidence", "finding"]
    source_id: int
    target_type: Literal["record", "work_item", "assessment", "evidence", "finding"]
    target_id: int
    relation: str = Field(min_length=3, max_length=50)
    rationale: str = Field(min_length=12, max_length=1000)


@app.get("/api/relationships")
def relationships(
    object_type: str | None = None,
    object_id: int | None = None,
    user=Depends(actor),
    s=Depends(db),
):
    query = select(Relationship).order_by(Relationship.id)
    if object_type and object_id:
        query = query.where(
            or_(
                (Relationship.source_type == object_type) & (Relationship.source_id == object_id),
                (Relationship.target_type == object_type) & (Relationship.target_id == object_id),
            )
        )
    return [encode(item) for item in s.scalars(query)]


@app.post("/api/relationships", status_code=201)
def create_relationship(data: RelationshipInput, user=Depends(actor), s=Depends(db)):
    permit(user, EDIT_ROLES | VERIFY_ROLES)
    edge = Relationship(**data.model_dump(), created_by=user.id, reviewed_by=user.id, created_at=now())
    s.add(edge)
    s.flush()
    activity(s, user, "relationship.created", edge.id, data.model_dump())
    s.commit()
    return encode(edge)


@app.get("/api/policy-acknowledgements")
def acknowledgements(policy_id: int | None = None, user=Depends(actor), s=Depends(db)):
    query = select(PolicyAcknowledgement).order_by(PolicyAcknowledgement.id)
    if policy_id:
        query = query.where(PolicyAcknowledgement.policy_id == policy_id)
    return [encode(item) for item in s.scalars(query)]


class Acknowledge(BaseModel):
    subject_ref: str = Field(min_length=2, max_length=80)


@app.post("/api/policy-acknowledgements/{id}/acknowledge")
def acknowledge(id: int, data: Acknowledge, user=Depends(actor), s=Depends(db)):
    item = fetch(s, PolicyAcknowledgement, id)
    if item.subject_ref not in {data.subject_ref, user.username} and user.role not in EDIT_ROLES:
        raise HTTPException(403, "Acknowledgement subject does not match signed-in user")
    item.status = "Acknowledged"
    item.acknowledged_at = now()
    item.recorded_by = user.id
    activity(s, user, "policy.acknowledged", item.policy_id, {"subject_ref": item.subject_ref})
    s.commit()
    return encode(item)


@app.get("/api/policies/effectiveness")
def policy_effectiveness(user=Depends(actor), s=Depends(db)):
    policies = list(s.scalars(select(WorkItem).where(WorkItem.domain == "policy")))
    acknowledgements = list(s.scalars(select(PolicyAcknowledgement)))
    by_policy = {}
    for item in acknowledgements:
        by_policy.setdefault(item.policy_id, []).append(item)
    rows = []
    for policy in policies:
        assigned = by_policy.get(policy.id, [])
        acknowledged = sum(item.status == "Acknowledged" for item in assigned)
        p = policy.payload
        rows.append(
            {
                "policy_id": policy.id,
                "uid": policy.uid,
                "title_ar": policy.title_ar,
                "title_en": policy.title_en,
                "document_exists": True,
                "approved": policy.status in {"Approved", "Published", "Expired", "Retired"},
                "published": policy.status == "Published",
                "acknowledged": acknowledged,
                "assigned": len(assigned),
                "acknowledgement_rate": round(100 * acknowledged / len(assigned), 1) if assigned else None,
                "procedure_implemented": bool(p.get("procedure_implemented")),
                "control_operating": bool(p.get("control_operating")),
                "evidence_verified": bool(p.get("evidence_verified")),
                "independently_tested": bool(p.get("independently_tested")),
                "test_frequency": p.get("test_frequency", "Not assigned"),
                "next_test_date": p.get("next_test_date"),
            }
        )
    return {"as_of": date.today().isoformat(), "policies": rows}
