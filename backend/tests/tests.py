from fastapi import APIRouter
from auth.request import authentication, AuthClaims

router = APIRouter(tags=["tests"])


@router.get("/tests/authenticate")
async def authentication(claims: AuthClaims):
    return claims
