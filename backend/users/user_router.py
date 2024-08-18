from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import AfterValidator
from . import Users
from models import UuidStr, UserModel
from auth.dep_functions import authentication_guard

router = APIRouter(tags=["users"], dependencies=[Depends(authentication_guard)])


@router.get("/users")
async def get_users():
    return Users.items()


@router.get("/users/{user_id}")
async def get_user(user_id: Annotated[UuidStr, Path()]):
    return Users.load(user_id)


@router.put("/users")
async def update_user(user: Annotated[UserModel, Body()]):
    return Users.update(user)


@router.delete("/users/{user_id}")
async def delete_user(user_id: Annotated[str, Path()]):
    return Users.remove(user_id)
