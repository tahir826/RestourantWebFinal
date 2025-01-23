from fastapi import APIRouter, HTTPException
from app.models.user import UserSignup, UserLogin
from app.db import Database
from app.utils.password import hash_password, verify_password
import uuid

router = APIRouter()

@router.post("/signup/")
async def signup(user: UserSignup):
    conn = Database.pool
    existing_user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)
    await conn.execute(
        "INSERT INTO users (user_id, email, username, password) VALUES ($1, $2, $3, $4)",
        user_id, user.email, user.username, hashed_password
    )
    return {"message": "User registered successfully.", "user_id": user_id}

@router.post("/login/")
async def login(user: UserLogin):
    conn = Database.pool
    db_user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", user.email)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    return {
        "message": "Login successful.",
        "user": {
            "user_id": db_user["user_id"],
            "email": db_user["email"],
            "username": db_user["username"],
        }
    }