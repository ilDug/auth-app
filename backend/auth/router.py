from typing import Annotated
from fastapi import Body, Cookie, APIRouter, Header, Query

from .auth import Auth
from .sign import sign_data, verify_signature
from models import DataWithSignature

router = APIRouter(tags=["auth"])

# #########################################
# from icecream import ic

# ic.configureOutput(includeContext=True)
# #########################################


@router.get("/auth/authenticate")
async def authenticate(
    authorization: Annotated[str | None, Header()] = None,
    claims: Annotated[
        bool | None, Query(description="Se True, restituisce i claims del token")
    ] = False,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
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


@router.post("/auth/sign")
async def sign(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
    data: Annotated[str | dict, Body(description="Dati da firmare")] = None,
):
    claims = Auth().authenticate(authorization, fingerprint, claims=True)
    return sign_data(claims["uid"], data)


@router.post("/auth/verify_signature")
async def verify(
    data: Annotated[DataWithSignature, Body(description="I dati firmati")],
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    """i dati devono contenere almeno una proprietà signature"""
    claims = Auth().authenticate(authorization, fingerprint, claims=True)
    return verify_signature(claims["uid"], data)
