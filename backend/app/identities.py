from .core import hashlib, PH, DUMMY_HASH, lock, attempts, app, db, actor, activity
import os
import secrets
from datetime import datetime, timedelta, timezone
from argon2.exceptions import VerificationError
from fastapi import Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from .db import User, LoginSession


class Login(BaseModel):
    username: str = Field(max_length=80)
    password: str = Field(max_length=200)


@app.get("/api/health")
def health(s=Depends(db)):
    s.execute(select(func.count(User.id)))
    return {"status": "ok", "version": "0.2.0", "deployment": "single-organization"}


@app.post("/api/login")
def login(data: Login, request: Request, response: Response, s=Depends(db)):
    key = request.client.host
    current = datetime.now(timezone.utc).timestamp()
    with lock:
        attempts[key] = [t for t in attempts[key] if current - t < 60]
        if len(attempts[key]) >= 10:
            raise HTTPException(429, "Try again after one minute")
        attempts[key].append(current)
    user = s.scalar(select(User).where(User.username == data.username))
    try:
        PH.verify(user.password if user else DUMMY_HASH, data.password)
    except VerificationError:
        raise HTTPException(401, "Invalid credentials")
    if not user:
        raise HTTPException(401, "Invalid credentials")
    token = secrets.token_urlsafe(48)
    s.add(
        LoginSession(
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            user_id=user.id,
            expires=(datetime.now(timezone.utc) + timedelta(hours=8)).isoformat(),
        )
    )
    with lock:
        activity(s, user, "session.created", "session")
        s.commit()
    response.set_cookie(
        "mizan_session",
        token,
        httponly=True,
        samesite="strict",
        secure=os.getenv("SECURE_COOKIES", "false") == "true",
        max_age=28800,
    )
    return {"id": user.id, "username": user.username, "role": user.role}


@app.get("/api/me")
def me(user=Depends(actor)):
    return {"id": user.id, "username": user.username, "role": user.role}


@app.post("/api/logout")
def logout(request: Request, response: Response, user=Depends(actor), s=Depends(db)):
    token = request.cookies.get("mizan_session", "")
    session = s.get(LoginSession, hashlib.sha256(token.encode()).hexdigest())
    if session:
        s.delete(session)
    s.commit()
    response.delete_cookie("mizan_session")
    return {"ok": True}


@app.get("/api/users")
def users(user=Depends(actor), s=Depends(db)):
    return [
        {"id": u.id, "username": u.username, "role": u.role}
        for u in s.scalars(select(User))
    ]


class RoleUpdate(BaseModel):
    role: str


@app.put("/api/users/{id}/role")
def update_role(id: int, data: RoleUpdate, user=Depends(actor), s=Depends(db)):
    from .core import READERS, fetch, permit

    permit(user, {"Super Admin"})
    if data.role not in READERS:
        raise HTTPException(422, "Unknown role")
    target = fetch(s, User, id)
    if target.id == user.id:
        raise HTTPException(409, "Use a second administrator to change your own role")
    previous = target.role
    target.role = data.role
    activity(
        s,
        user,
        "identity.role_changed",
        target.username,
        {"from": previous, "to": data.role},
    )
    s.commit()
    return {"id": target.id, "username": target.username, "role": target.role}
