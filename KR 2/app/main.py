from fastapi import FastAPI, HTTPException, Request, Response, Depends, Cookie, Header
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from pydantic import ValidationError
import uuid
import time
from datetime import datetime
from typing import Optional, List

from . import models
from .products_data import products
from .config import TEST_USERNAME, TEST_PASSWORD, SECRET_KEY

serializer = URLSafeTimedSerializer(SECRET_KEY)
sessions_db = {}

app = FastAPI(title="Вторая контрольная работа")

@app.get("/products/search")
async def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10
) -> List[dict]:
    results = []
    for product in products:
        if keyword.lower() not in product["name"].lower():
            continue
        if category and product["category"].lower() != category.lower():
            continue
        results.append(product)
    return results[:limit]

@app.get("/product/{product_id}")
async def get_product(product_id: int) -> dict:
    for product in products:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Товар не найден")

def verify_credentials(username: str, password: str) -> bool:
    return username == TEST_USERNAME and password == TEST_PASSWORD

def create_signed_session_token(user_id: str, timestamp: int = None) -> str:
    if timestamp is None:
        timestamp = int(time.time())
    data = f"{user_id}.{timestamp}"
    signature = serializer.dumps(data)
    return signature

def verify_signed_session_token(token: str) -> tuple[str, int]:
    try:
        data = serializer.loads(token, max_age=300)
        parts = data.split(".")
        if len(parts) != 2:
            raise BadSignature("Invalid token format")
        user_id = parts[0]
        timestamp = int(parts[1])
        return user_id, timestamp
    except (SignatureExpired, BadSignature, ValueError):
        raise HTTPException(status_code=401, detail="Invalid session token")

def get_session_token_from_cookie(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return session_token

@app.post("/login")
async def login(request: Request, response: Response, login_data: models.LoginRequest):
    if not verify_credentials(login_data.username, login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(uuid.uuid4())
    current_timestamp = int(time.time())
    signed_token = create_signed_session_token(user_id, current_timestamp)
    
    sessions_db[signed_token] = {
        "user_id": user_id,
        "last_activity": current_timestamp
    }
    
    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=300,
        secure=False,
        samesite="lax"
    )
    
    return {"message": "Login successful"}

@app.get("/profile")
async def get_profile(
    request: Request,
    response: Response,
    session_token: str = Depends(get_session_token_from_cookie)
):
    try:
        user_id, token_timestamp = verify_signed_session_token(session_token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session_data = sessions_db.get(session_token)
    if not session_data or session_data["user_id"] != user_id:
        raise HTTPException(status_code=401, detail="Session not found")
    
    last_activity = session_data["last_activity"]
    current_time = int(time.time())
    time_since_last = current_time - last_activity
    
    if time_since_last >= 300:
        del sessions_db[session_token]
        raise HTTPException(status_code=401, detail="Session expired")
    
    should_extend = False
    if 180 <= time_since_last < 300:
        should_extend = True
    
    if should_extend:
        new_timestamp = current_time
        sessions_db[session_token]["last_activity"] = new_timestamp
        new_signed_token = create_signed_session_token(user_id, new_timestamp)
        
        response.set_cookie(
            key="session_token",
            value=new_signed_token,
            httponly=True,
            max_age=300,
            secure=False,
            samesite="lax"
        )
        
        sessions_db[new_signed_token] = sessions_db.pop(session_token)
    
    return {
        "message": "Profile accessed successfully",
        "user_id": user_id,
        "last_activity": datetime.fromtimestamp(sessions_db[session_token]["last_activity"]).isoformat()
    }

@app.post("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token and session_token in sessions_db:
        del sessions_db[session_token]
    response.delete_cookie("session_token", httponly=True)
    return {"message": "Logout successful"}

@app.get("/5.4/headers")
async def headers_54(
    user_agent: str = Header(..., alias="User-Agent"),
    accept_language: str = Header(..., alias="Accept-Language")
):
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }

@app.get("/5.5/headers")
async def headers_55(headers: models.CommonHeaders = Depends()):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@app.get("/5.5/info")
async def info_55(
    response: Response,
    headers: models.CommonHeaders = Depends()
):
    response.headers["X-Server-Time"] = datetime.now().isoformat()
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )