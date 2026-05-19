from fastapi import HTTPException, Header, Depends
from .schemas import User
from .storage import storage

async def get_current_user(x_user_id: int = Header(...), x_user_role: str = Header("user")) -> User:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header is required")
    return User(id=x_user_id, role=x_user_role)

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

async def get_storage():
    return storage