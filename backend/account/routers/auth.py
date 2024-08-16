from typing import Annotated
from fastapi import Cookie, APIRouter, Header, Path, Query
from auth import Auth

router = APIRouter(tags=["auth"])


@router.get("/auth/authenticate")
async def authenticate(
    authorization: Annotated[str | None, Header()] = None,
    claims: Annotated[
        bool | None, Query(description="Se True, restituisce i claims del token")
    ] = False,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    # print(f"cookie fingerprint for JWT is: {fingerprint}")
    # print(f"query param per i CLAIM = {claims}")
    claims = Auth().authenticate(authorization, fingerprint, claims=claims)
    return claims


@router.get("/auth/authorize")
async def authorization_check(
    authorization: Annotated[str | None, Header()] = None,
    permission: Annotated[
        str, Query(description="il permesso o il ruolo da verificare")
    ] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    if permission is None:
        return False
    return Auth().authorize(authorization, fingerprint, permission)
