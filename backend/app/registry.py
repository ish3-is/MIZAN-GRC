from fastapi import Depends
from sqlalchemy import select
from .db import Record
from .core import app, db, actor, encode


@app.get("/api/records/{kind}")
def records(kind: str, user=Depends(actor), s=Depends(db)):
    return [
        encode(r)
        for r in s.scalars(
            select(Record).where(Record.kind == kind).order_by(Record.id)
        )
    ]
