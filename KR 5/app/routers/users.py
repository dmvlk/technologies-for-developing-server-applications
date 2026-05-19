from fastapi import APIRouter, Depends, HTTPException
from ..schemas import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return User(id=user_id, role="user")