import hashlib
import json
import os
import secrets
import threading
from collections import defaultdict
from pathlib import Path
from contextlib import asynccontextmanager

from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from .db import Session, User, LoginSession, Record, Activity, now

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.getenv("EVIDENCE_DIR", "./data/evidence"))
PH = PasswordHasher()
DUMMY_HASH = PH.hash(secrets.token_urlsafe(32))
lock = threading.RLock()
attempts = defaultdict(list)
READERS = {
    "Super Admin",
    "GRC Manager",
    "GRC Analyst",
    "Compliance Officer",
    "Risk Manager",
    "Risk Owner",
    "Privacy Officer",
    "Control Owner",
    "Internal Auditor",
    "Executive Viewer",
}
EDITORS = {
    "Super Admin",
    "GRC Manager",
    "GRC Analyst",
    "Compliance Officer",
    "Control Owner",
}
REVIEWERS = {"GRC Manager", "Internal Auditor"}


@asynccontextmanager
async def lifespan(app):
    DATA.mkdir(parents=True, exist_ok=True)
    if not os.getenv("EVIDENCE_KEY"):
        raise RuntimeError("EVIDENCE_KEY must be configured; run scripts/bootstrap.ps1")
    Fernet(os.environ["EVIDENCE_KEY"].encode())
    yield


app = FastAPI(
    title="MIZAN GRC",
    version="0.2.0",
    lifespan=lifespan,
    description="Single organization research demonstrator. Compliance management, not certification or legal advice.",
)


@app.middleware("http")
async def security(request: Request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        configured = os.getenv("APP_ORIGINS") or os.getenv("APP_ORIGIN")
        allowed = (
            {value.strip() for value in configured.split(",")}
            if configured
            else {
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174",
            }
        )
        if origin and origin not in allowed:
            return JSONResponse(
                {
                    "detail": "Browser address is not allowed. Open the configured application URL."
                },
                status_code=403,
            )
        if (
            request.url.path != "/api/login"
            and request.headers.get("x-mizan-request") != "1"
        ):
            return Response("CSRF request header required", status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Frame-Options"] = "DENY"
    return response


def db():
    with Session() as s:
        yield s


def actor(request: Request, s=Depends(db)):
    token = request.cookies.get("mizan_session", "")
    session = s.get(LoginSession, hashlib.sha256(token.encode()).hexdigest())
    if not session or session.expires < now():
        raise HTTPException(401, "Sign in required")
    user = s.get(User, session.user_id)
    if not user or user.role not in READERS:
        raise HTTPException(403, "Role denied")
    return user


def permit(user, roles):
    if user.role not in roles:
        raise HTTPException(403, "Role cannot perform this action")


def fetch(s, model, id):
    item = s.scalar(select(model).where(model.id == id).with_for_update())
    if not item:
        raise HTTPException(404, "Record not found")
    return item


def document(s, id, kind):
    item = fetch(s, Record, id)
    if item.kind != kind:
        raise HTTPException(422, f"Expected {kind}")
    return item


def encode(item):
    return {c.name: getattr(item, c.name) for c in item.__table__.columns}


def activity(s, user, action, target, details=None):
    # A PostgreSQL transaction advisory lock serializes the hash chain across workers.
    if s.bind.dialect.name == "postgresql":
        from sqlalchemy import text

        s.execute(text("SELECT pg_advisory_xact_lock(712039)"))
    previous = s.scalar(select(Activity).order_by(Activity.id.desc()).limit(1))
    event = Activity(
        actor=user.username,
        action=action,
        target=str(target),
        created=now(),
        details=details or {},
        previous_hash=previous.digest if previous else "0" * 64,
    )
    event.digest = event_hash(event)
    s.add(event)


def event_hash(e):
    content = {
        k: getattr(e, k)
        for k in ("actor", "action", "target", "created", "details", "previous_hash")
    }
    return hashlib.sha256(
        json.dumps(content, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
