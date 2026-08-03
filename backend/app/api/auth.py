from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.security import create_token, current_user, hash_password, verify_password
from app.core.storage import connection, row_dict

router = APIRouter()
class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)
    role: str = "Viewer"

class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)

@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    role = body.role.title()
    if role not in {"Admin", "Analyst", "Viewer"}: raise HTTPException(422, "Role must be Admin, Analyst, or Viewer")
    try:
        with connection() as conn:
            cursor = conn.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)", (body.name.strip(), body.email.lower(), hash_password(body.password), role))
            user_id = cursor.lastrowid
    except Exception as exc:
        raise HTTPException(409, "An account with that email already exists") from exc
    return {"access_token": create_token(str(user_id), role), "token_type": "bearer", "user": {"id": user_id, "name": body.name.strip(), "email": body.email.lower(), "role": role}}

@router.post("/login")
def login(body: LoginRequest):
    with connection() as conn: user = row_dict(conn.execute("SELECT * FROM users WHERE email=?", (body.email.lower(),)).fetchone())
    if not user or not verify_password(body.password, user["password_hash"]): raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_token(str(user["id"]), user["role"]), "token_type": "bearer", "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}}

@router.post("/logout", status_code=204)
def logout(_: dict = Depends(current_user)): return None

@router.get("/me")
def me(token: dict = Depends(current_user)):
    with connection() as conn: user = row_dict(conn.execute("SELECT id,name,email,role,created_at FROM users WHERE id=?", (token["sub"],)).fetchone())
    if not user: raise HTTPException(401, "User no longer exists")
    return user
