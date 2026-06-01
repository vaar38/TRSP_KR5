from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(user: UserOut = Depends(get_current_user)):
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, current_user: UserOut = Depends(get_current_user)):
    # Simple stub — returns a user object for any valid user_id
    return UserOut(id=user_id, role="user")
