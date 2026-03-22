from fastapi import FastAPI, HTTPException, Response, Cookie
from pydantic import BaseModel
import uuid
from itsdangerous import URLSafeTimedSerializer
from typing import Optional

app = FastAPI()

SECRET_KEY = "secret-key"
serializer = URLSafeTimedSerializer(SECRET_KEY)

VALID_USERS = {
    "user123": "password123"
}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(response: Response, login_data: LoginRequest):
    if login_data.username not in VALID_USERS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if VALID_USERS[login_data.username] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user_id = str(uuid.uuid4())
    
    session_token = serializer.dumps(user_id)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=3600,
        secure=False
    )
    
    return {"message": "Login successful", "user_id": user_id}


@app.get("/profile")
async def get_profile(session_token: Optional[str] = Cookie(None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
    
    try:
        user_id = serializer.loads(session_token, max_age=3600)
        
        return {
            "user_id": user_id,
            "username": "user123",
            "profile": "User profile information",
            "message": "Authentication successful"
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
