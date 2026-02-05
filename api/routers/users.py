from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, Path
from controllers.users import Users
from models import UuidStr
from core import PERMISSIONS
from controllers.auth import AuthenticationGuard, AuthPermissions

router = APIRouter(
    tags=["users"],
    prefix="/api/auth/v2/users",
)


@router.get("/")
async def get_users(_: AuthenticationGuard):
    return await Users.items()


@router.get("/{user_id}")
async def get_user(user_id: Annotated[UuidStr, Path()], _: AuthenticationGuard):
    return await Users.load(user_id)


@router.put("/")
async def update_user(user: Annotated[dict, Body()], permissions: AuthPermissions):
    if PERMISSIONS.USER_ADMIN.value in permissions:
        return await Users.update(user)
    else:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions, only user admins can update users",
        )


@router.delete("/{user_id}")
async def delete_user(user_id: Annotated[str, Path()], permissions: AuthPermissions):
    if PERMISSIONS.USER_ADMIN.value in permissions:
        return await Users.remove(user_id)
    else:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions, only user admins can delete users",
        )
