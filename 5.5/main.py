from fastapi import FastAPI, Header, HTTPException
import re
from typing import Optional

app = FastAPI()

@app.get("/headers")
async def get_headers(
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None)
):
    if user_agent is None:
        raise HTTPException(status_code=400, detail="User-Agent header is required")
    
    if accept_language is None:
        raise HTTPException(status_code=400, detail="Accept-Language header is required")
    
    pattern = r'^[a-zA-Z0-9\-_;,=/.]+$'
    if not re.match(pattern, accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }
