from datetime import date
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from .db import User, Assessment, Finding
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


class FindingInput(BaseModel):
    assessment_id: int
    risk_id: int
    title: str = Field(min_length=5, max_length=240)
    action: str = Field(min_length=10, max_length=4000)
    owner_id: int
    due: date


@app.post("/api/findings", status_code=201)
def create_finding(data: FindingInput, user=Depends(actor), s=Depends(db)):
    permit(user, EDITORS | {"Internal Auditor"})
    fetch(s, Assessment, data.assessment_id)
    document(s, data.risk_id, "risk")
    fetch(s, User, data.owner_id)
    f = Finding(**(data.model_dump() | {"due": data.due.isoformat()}))
    with lock:
        s.add(f)
        s.flush()
        activity(s, user, "finding.created", f.id)
        s.commit()
    return encode(f)


@app.get("/api/findings")
def findings(user=Depends(actor), s=Depends(db)):
    return [encode(f) for f in s.scalars(select(Finding))]


class FindingTransition(BaseModel):
    state: Literal["In Progress", "Ready for Retest", "Closed"]
    rationale: str = Field(min_length=10, max_length=2000)


@app.post("/api/findings/{id}/transition")
def transition(id: int, data: FindingTransition, user=Depends(actor), s=Depends(db)):
    with lock:
        f = fetch(s, Finding, id)
        if data.state == "Closed":
            permit(user, REVIEWERS)
            a = fetch(s, Assessment, f.assessment_id)
            if (
                user.id in {f.owner_id, a.owner_id}
                or f.state != "Ready for Retest"
                or a.stage != "Approved"
                or a.status != "Compliant"
            ):
                raise HTTPException(
                    409, "Independent retest and approved compliant assessment required"
                )
        else:
            permit(user, EDITORS)
            if user.id != f.owner_id or (f.state, data.state) not in {
                ("Open", "In Progress"),
                ("In Progress", "Ready for Retest"),
            }:
                raise HTTPException(409, "Owner and valid transition required")
        f.state = data.state
        activity(s, user, "finding.transition", id, data.model_dump())
        s.commit()
    return encode(f)
