from datetime import date
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field
from .db import Record, now
from .core import lock, app, db, actor, permit, document, encode, activity


class RiskInput(BaseModel):
    title: str = Field(min_length=5, max_length=240)
    department: str = Field(min_length=2, max_length=80)
    asset_id: int
    inherent_likelihood: int = Field(ge=1, le=5)
    inherent_impact: int = Field(ge=1, le=5)
    residual_likelihood: int = Field(ge=1, le=5)
    residual_impact: int = Field(ge=1, le=5)
    inherent_rationale: str = Field(min_length=10, max_length=2000)
    control_effectiveness_rationale: str = Field(min_length=10, max_length=2000)
    residual_rationale: str = Field(min_length=10, max_length=2000)
    treatment: Literal["mitigate", "avoid", "transfer", "accept"]


@app.post("/api/risks", status_code=201)
def create_risk(data: RiskInput, user=Depends(actor), s=Depends(db)):
    permit(user, {"Super Admin", "GRC Manager", "Risk Manager", "Privacy Officer"})
    document(s, data.asset_id, "asset")
    payload = data.model_dump(exclude={"title", "department"}) | {
        "assessed_at": now(),
        "owner_id": user.id,
        "acceptance": "Pending" if data.treatment == "accept" else None,
    }
    r = Record(
        kind="risk", title=data.title, department=data.department, payload=payload
    )
    with lock:
        s.add(r)
        s.flush()
        activity(s, user, "risk.created", r.id, payload)
        s.commit()
    return encode(r)


class Acceptance(BaseModel):
    rationale: str = Field(min_length=10, max_length=2000)
    review_date: date


@app.post("/api/risks/{id}/accept")
def accept(id: int, data: Acceptance, user=Depends(actor), s=Depends(db)):
    permit(user, {"GRC Manager"})
    with lock:
        r = document(s, id, "risk")
        if (
            r.payload.get("owner_id") == user.id
            or r.payload.get("treatment") != "accept"
            or data.review_date <= date.today()
        ):
            raise HTTPException(
                409,
                "Independent acceptance, acceptance treatment and future review date required",
            )
        r.payload = r.payload | {
            "acceptance": "Approved",
            "acceptance_approver": user.id,
            "acceptance_rationale": data.rationale,
            "acceptance_review": data.review_date.isoformat(),
        }
        r.version += 1
        activity(s, user, "risk.accepted", id, r.payload)
        s.commit()
    return encode(r)
