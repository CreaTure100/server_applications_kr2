from fastapi import FastAPI, HTTPException, Response, Cookie, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import uuid
from typing import Optional

app = FastAPI()

sessions_db = {}

class LoginRequest(BaseModel):
    username: str
    password: str

VALID_USERS = {
    "user123": "password123",
    "admin": "adminpass"
}

@app.post("/login")
async def login(response: Response, login_data: LoginRequest):
    if login_data.username not in VALID_USERS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if VALID_USERS[login_data.username] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    session_token = str(uuid.uuid4())
    
    sessions_db[session_token] = login_data.username
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=1000,
        secure=False
    )
    
    return {"message": "Login successful", "session_token": session_token}


@app.get("/user")
async def get_user(session_token: Optional[str] = Cookie(None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
    
    if session_token not in sessions_db:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
    
    username = sessions_db[session_token]
    
    return {
        "username": username,
        "message": "Profile information",
        "session_token": session_token
    }
