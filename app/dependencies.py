from fastapi import Header, HTTPException
from app.schemas import UserOut
from app.storage import task_storage, TaskStorage


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> UserOut:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    try:
        user_id = int(x_user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid X-User-Id header")
    role = x_user_role if x_user_role else "user"
    return UserOut(id=user_id, role=role)


def require_admin(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> UserOut:
    user = get_current_user(x_user_id, x_user_role)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_storage() -> TaskStorage:
    return task_storage
