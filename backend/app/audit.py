from fastapi import Depends
from sqlalchemy import select
from .db import Activity
from .core import app, db, actor, permit, encode, event_hash


@app.get("/api/activity")
def audit_log(user=Depends(actor), s=Depends(db)):
    permit(user, {"Super Admin", "GRC Manager", "Internal Auditor"})
    return [
        encode(e)
        for e in s.scalars(select(Activity).order_by(Activity.id.desc()).limit(500))
    ]


@app.get("/api/activity/verify")
def verify_log(user=Depends(actor), s=Depends(db)):
    permit(user, {"Super Admin", "GRC Manager", "Internal Auditor"})
    previous, count = "0" * 64, 0
    for e in s.scalars(select(Activity).order_by(Activity.id)):
        if e.previous_hash != previous or e.digest != event_hash(e):
            return {"valid": False, "failed_id": e.id, "count": count}
        previous = e.digest
        count += 1
    return {
        "valid": True,
        "count": count,
        "head": previous,
        "limitation": "Requires external head anchoring to detect chain truncation or wholesale rewrite by a database administrator.",
    }
