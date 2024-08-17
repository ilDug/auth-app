from fastapi import APIRouter
from auth_service import AuthClaims, UserId, AuthPermissions, AuthorizeFn

router = APIRouter(tags=["tests"])


@router.get("/tests/authenticate")
async def authentication(claims: AuthClaims):
    return claims


@router.get("/tests/user_id")
async def user_id(user_id: UserId):
    return user_id


@router.get("/tests/permissions")
async def permissions(permissions: AuthPermissions):
    return permissions


@router.get("/tests/authorize")
async def authorization(is_authorized: AuthorizeFn):
    return await is_authorized("basic")
