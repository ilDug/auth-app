from typing import Annotated
from fastapi import Body, Cookie, APIRouter, HTTPException, Header, Query
from datetime import datetime
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
    # se non c'è il permesso nei parametri della richiesta, non autorizza
    if permission is None:
        return False

    auth = Auth()
    # prima prova a vedere se è admin (ACCESSO COMPLETO A TUTTO)
    try:
        is_admin = auth.authorize(authorization, fingerprint, "admin")
    except Exception:
        is_admin = False
    finally:
        return (
            True if is_admin else auth.authorize(authorization, fingerprint, permission)
        )


@router.post("/auth/sign")
async def sign(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
    data: Annotated[str | dict, Body(description="Dati da firmare")] = None,
    on: Annotated[
        str, Query(description="la data della firma, nel formato yyyy-mm-dd")
    ] = None,
):
    try:
        date = datetime.strptime(on, "%Y-%m-%d") if on is not None else datetime.now()
    except ValueError as e:
        raise HTTPException(400, "Data non valida")

    claims = Auth().authenticate(authorization, fingerprint, claims=True)
    return sign_data(claims["uid"], data, date)


@router.post("/auth/verify_signature")
async def verify(
    data: Annotated[DataWithSignature, Body(description="I dati firmati")],
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    """i dati devono contenere almeno una proprietà signature"""
    claims = Auth().authenticate(authorization, fingerprint, claims=True)
    return verify_signature(claims["uid"], data)
