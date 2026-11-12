from datetime import date
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from .db import Assessment, Evidence
from .core import (
    lock,
    EDITORS,
    REVIEWERS,
    app,
    db,
    actor,
    permit,
    fetch,
    document,
    encode,
    activity,
)
from .evidence import decrypt_evidence


class NewAssessment(BaseModel):
    control_id: int
    asset_id: int
    period: str = Field(default="2026-Q4", min_length=4, max_length=30)


@app.post("/api/assessments", status_code=201)
def create_assessment(data: NewAssessment, user=Depends(actor), s=Depends(db)):
    permit(user, EDITORS)
    document(s, data.control_id, "control")
    document(s, data.asset_id, "asset")
    a = Assessment(**data.model_dump(), owner_id=user.id)
    with lock:
        s.add(a)
        s.flush()
        activity(s, user, "assessment.created", a.id)
        s.commit()
    return encode(a)


@app.get("/api/assessments")
def assessments(user=Depends(actor), s=Depends(db)):
    return [encode(a) for a in s.scalars(select(Assessment).order_by(Assessment.id))]


class AssessmentUpdate(BaseModel):
    status: Literal[
        "Not Assessed",
        "Not Applicable",
        "Compliant",
        "Partially Compliant",
        "Non-Compliant",
        "Pending Verification",
    ]
    rationale: str = Field(min_length=10, max_length=4000)
    version: int


@app.put("/api/assessments/{id}")
def update_assessment(
    id: int, data: AssessmentUpdate, user=Depends(actor), s=Depends(db)
):
    permit(user, EDITORS)
    with lock:
        a = fetch(s, Assessment, id)
        if a.owner_id != user.id:
            raise HTTPException(403, "Assessment owner required")
        if a.stage not in ("Draft", "Returned") or a.version != data.version:
            raise HTTPException(409, "Assessment is locked or changed; refresh")
        a.status, a.rationale = data.status, data.rationale
        a.version += 1
        activity(s, user, "assessment.updated", id, data.model_dump())
        s.commit()
    return encode(a)


@app.post("/api/assessments/{id}/submit")
def submit(id: int, user=Depends(actor), s=Depends(db)):
    permit(user, EDITORS)
    with lock:
        a = fetch(s, Assessment, id)
        if a.owner_id != user.id:
            raise HTTPException(403, "Only the assessment owner may submit")
        if (
            a.stage not in ("Draft", "Returned")
            or len(a.rationale) < 10
            or a.status in ("Not Assessed", "Pending Verification")
        ):
            raise HTTPException(409, "Complete assessment before submission")
        if a.status != "Not Applicable" and not s.scalar(
            select(Evidence.id).where(Evidence.assessment_id == id)
        ):
            raise HTTPException(409, "Evidence required")
        a.stage = "Submitted"
        a.version += 1
        activity(s, user, "assessment.submitted", id)
        s.commit()
    return encode(a)


class Review(BaseModel):
    decision: Literal["approve", "return"]
    rationale: str = Field(min_length=10, max_length=4000)


@app.post("/api/assessments/{id}/review")
def review(id: int, data: Review, user=Depends(actor), s=Depends(db)):
    permit(user, REVIEWERS)
    with lock:
        a = fetch(s, Assessment, id)
        if a.owner_id == user.id:
            raise HTTPException(403, "Independent reviewer required")
        if a.stage != "Submitted":
            raise HTTPException(409, "Submit for review first")
        if data.decision == "approve" and a.status != "Not Applicable":
            evidence = list(
                s.scalars(select(Evidence).where(Evidence.assessment_id == id))
            )
            fresh = [e for e in evidence if e.review_due >= date.today().isoformat()]
            if not fresh:
                raise HTTPException(409, "Fresh evidence required for approval")
            for e in fresh:
                decrypt_evidence(e)
        a.stage = "Approved" if data.decision == "approve" else "Returned"
        a.reviewer_id = user.id
        a.version += 1
        activity(s, user, "assessment.reviewed", id, data.model_dump())
        s.commit()
    return encode(a)


@app.post("/api/assessments/{id}/reopen")
def reopen(id: int, user=Depends(actor), s=Depends(db)):
    permit(user, EDITORS)
    with lock:
        a = fetch(s, Assessment, id)
        if a.owner_id != user.id or a.stage != "Approved":
            raise HTTPException(409, "Owner of approved assessment required")
        activity(s, user, "assessment.reassessment", id, encode(a))
        a.stage = "Draft"
        a.reviewer_id = None
        a.version += 1
        s.commit()
    return encode(a)
