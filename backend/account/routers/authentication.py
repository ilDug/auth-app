from typing import Annotated
from fastapi import Cookie, APIRouter, Header, Query
from core.auth import Auth

router = APIRouter(tags=["auth"])


@router.get("/auth/authenticate")
async def authenticate(
    authorization: Annotated[str | None, Header()] = None,
    claims: Annotated[bool | None, Query()] = False,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    print(f"cookie fingerprint for JWT is: {fingerprint}")
    print(f"query param per i CLAIM = {claims}")
    claims = Auth().authenticate(authorization, fingerprint, claims=claims)
    return claims
