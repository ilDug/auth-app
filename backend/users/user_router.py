from typing import Annotated
from fastapi import APIRouter, Body, Path
from . import Users

router = APIRouter(tags=["users"])


@router.get("/users")
async def get_users():
    return Users.items()


@router.get("/users/{user_id}")
async def get_user(user_id: Annotated[str, Path()]):
    pass


@router.post("/users")
async def create_user(user: Annotated[dict, Body()]):
    pass


@router.put("/users")
async def update_user(user: Annotated[dict, Body()]):
    pass


@router.delete("/users/{user_id}")
async def delete_user(user_id: Annotated[str, Path()]):
    pass
