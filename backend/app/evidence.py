from .core import (
    hashlib,
    DATA,
    lock,
    READERS,
    EDITORS,
    app,
    db,
    actor,
    permit,
    fetch,
    encode,
    activity,
)
import os
import secrets
from datetime import date
from pathlib import Path
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Response, UploadFile, File, Form
from sqlalchemy import select
from .db import Assessment, Evidence


def decrypt_evidence(e):
    try:
        data = Fernet(os.environ["EVIDENCE_KEY"].encode()).decrypt(
            (DATA / e.storage_key).read_bytes()
        )
        if hashlib.sha256(data).hexdigest() != e.sha256:
            raise ValueError("Digest mismatch")
        return data
    except Exception:
        raise HTTPException(409, "Evidence integrity verification failed")


@app.post("/api/assessments/{id}/evidence", status_code=201)
async def upload(
    id: int,
    file: UploadFile = File(...),
    review_due: date = Form(...),
    user=Depends(actor),
    s=Depends(db),
):
    permit(user, EDITORS)
    a = fetch(s, Assessment, id)
    if a.owner_id != user.id or a.stage not in ("Draft", "Returned"):
        raise HTTPException(403, "Owner of an editable assessment required")
    name = Path((file.filename or "").replace("\\", "/")).name
    if len(name) > 120 or Path(name).suffix.lower() not in {
        ".txt",
        ".csv",
        ".pdf",
        ".png",
    }:
        raise HTTPException(
            422, "Allowed: TXT, CSV, PDF, PNG; max filename 120 characters"
        )
    content = await file.read(5 * 1024 * 1024 + 1)
    if not content or len(content) > 5 * 1024 * 1024:
        raise HTTPException(413, "Evidence must be 1 byte to 5 MB")
    if Path(name).suffix.lower() == ".pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(422, "Invalid PDF signature")
    if Path(name).suffix.lower() == ".png" and not content.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        raise HTTPException(422, "Invalid PNG signature")
    if Path(name).suffix.lower() in {".txt", ".csv"}:
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(422, "Text evidence must use UTF-8")
    storage = secrets.token_hex(24)
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / storage).write_bytes(
        Fernet(os.environ["EVIDENCE_KEY"].encode()).encrypt(content)
    )
    e = Evidence(
        assessment_id=id,
        filename=name,
        sha256=hashlib.sha256(content).hexdigest(),
        storage_key=storage,
        uploaded_by=user.id,
        review_due=review_due.isoformat(),
    )
    with lock:
        s.add(e)
        s.flush()
        activity(
            s, user, "evidence.uploaded", e.id, {"sha256": e.sha256, "assessment": id}
        )
        s.commit()
    return {k: v for k, v in encode(e).items() if k != "storage_key"}


@app.get("/api/evidence")
def evidence(user=Depends(actor), s=Depends(db)):
    return [
        {k: v for k, v in encode(e).items() if k != "storage_key"}
        for e in s.scalars(select(Evidence))
    ]


@app.get("/api/evidence/{id}/download")
def download(id: int, user=Depends(actor), s=Depends(db)):
    permit(user, READERS - {"Executive Viewer"})
    e = fetch(s, Evidence, id)
    data = decrypt_evidence(e)
    with lock:
        activity(s, user, "evidence.downloaded", id)
        s.commit()
    return Response(
        data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="evidence-{id}{Path(e.filename).suffix}"'
        },
    )
