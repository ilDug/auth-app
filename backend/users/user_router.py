from typing import Annotated
from fastapi import APIRouter, Body, Path
from pydantic import AfterValidator
from . import Users
from models import UuidStr, UserModel

router = APIRouter(tags=["users"])


@router.get("/users")
async def get_users():
    return Users.items()


@router.get("/users/{user_id}")
async def get_user(user_id: Annotated[UuidStr, Path()]):
    return Users.load(user_id)


@router.put("/users")
async def update_user(user: Annotated[UserModel, Body()]):
    pass


@router.delete("/users/{user_id}")
async def delete_user(user_id: Annotated[str, Path()]):
    pass
