from fastapi import FastAPI, HTTPException, Response, Cookie
from pydantic import BaseModel
import uuid
import time
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from typing import Optional

app = FastAPI()

SECRET_KEY = "secret-key"
serializer = URLSafeTimedSerializer(SECRET_KEY)

VALID_USERS = {
    "user123": "password123"
}

last_activity_db = {}

class LoginRequest(BaseModel):
    username: str
    password: str

def create_session_token(user_id: str, timestamp: int) -> str:
    data = f"{user_id}.{timestamp}"
    signature = serializer.dumps(data)
    return signature

def verify_session_token(token: str) -> tuple[str, int]:
    try:
        data = serializer.loads(token, max_age=300)
        parts = data.split('.')
        if len(parts) != 2:
            raise BadSignature("Invalid format")
        
        user_id = parts[0]
        timestamp = int(parts[1])
        
        return user_id, timestamp
    
    except (SignatureExpired, BadSignature, Exception) as e:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})

def should_update_session(last_timestamp: int, current_timestamp: int) -> bool:
    time_diff = current_timestamp - last_timestamp
    
    if time_diff >= 300:
        return None
    elif time_diff >= 180:
        return True
    else:
        return False

@app.post("/login")
async def login(response: Response, login_data: LoginRequest):
    if login_data.username not in VALID_USERS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if VALID_USERS[login_data.username] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user_id = str(uuid.uuid4())
    current_time = int(time.time())
    last_activity_db[user_id] = current_time
    session_token = create_session_token(user_id, current_time)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=300,
        secure=False
    )
    
    return {"message": "Login successful", "user_id": user_id}

@app.get("/profile")
async def get_profile(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
    
    try:
        user_id, cookie_timestamp = verify_session_token(session_token)
        
        if user_id not in last_activity_db:
            raise HTTPException(status_code=401, detail={"message": "Invalid session"})
        
        last_timestamp = last_activity_db[user_id]
        current_timestamp = int(time.time())
        
        if cookie_timestamp != last_timestamp:
            raise HTTPException(status_code=401, detail={"message": "Invalid session"})
        
        update_needed = should_update_session(last_timestamp, current_timestamp)
        
        if update_needed is None:
            del last_activity_db[user_id]
            raise HTTPException(status_code=401, detail={"message": "Session expired"})
        
        if update_needed:
            new_timestamp = current_timestamp
            last_activity_db[user_id] = new_timestamp
            
            new_session_token = create_session_token(user_id, new_timestamp)
            
            response.set_cookie(
                key="session_token",
                value=new_session_token,
                httponly=True,
                max_age=300,
                secure=False
            )
            
            return {
                "user_id": user_id,
                "username": "user123",
                "profile": "User profile information",
                "session_updated": True,
                "message": "Session extended"
            }
        else:
            return {
                "user_id": user_id,
                "username": "user123",
                "profile": "User profile information",
                "session_updated": False,
                "message": "Session valid"
            }
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})
