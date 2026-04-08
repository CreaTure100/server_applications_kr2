from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re
from typing import Optional

app = FastAPI()

class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")
    
    @validator('accept_language')
    def validate_accept_language(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Accept-Language header is required')
        
        pattern = r'^[a-zA-Z0-9\-_;,=/.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Accept-Language format')
        
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('Accept-Language must contain at least one language tag')
        
        return v
    
    model_config = {
        "populate_by_name": True
    }


@app.get("/headers")
async def get_headers(
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None)
):
    if user_agent is None:
        raise HTTPException(status_code=400, detail="User-Agent header is required")
    
    if accept_language is None:
        raise HTTPException(status_code=400, detail="Accept-Language header is required")
    
    try:
        CommonHeaders(
            user_agent=user_agent,
            accept_language=accept_language
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


@app.get("/info")
async def get_info(
    response: Response,
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None)
):
    if user_agent is None:
        raise HTTPException(status_code=400, detail="User-Agent header is required")
    
    if accept_language is None:
        raise HTTPException(status_code=400, detail="Accept-Language header is required")
    
    try:
        CommonHeaders(
            user_agent=user_agent,
            accept_language=accept_language
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    current_time = datetime.now().isoformat()
    response.headers["X-Server-Time"] = current_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": user_agent,
            "Accept-Language": accept_language
        }
    }
