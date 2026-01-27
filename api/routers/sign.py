from typing import Annotated
from fastapi import Body, Cookie, HTTPException, Header, Query, APIRouter
from controllers.auth import Auth
from controllers.sign import sign_data, verify_signature
from models import DataWithSignature
from datetime import datetime

router = APIRouter(tags=["signature"], prefix="/api/v1/sign")


@router.post("/sign")
async def sign(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
    data: Annotated[str | dict, Body(description="Dati da firmare")] = None,
    on: Annotated[
        str, Query(description="la data della firma, nel formato yyyy-mm-dd")
    ] = None,
):
    try:
        #  verifica che la data sia formattata in modo corretto.
        #  ad ogni modo utilizza la stringa "on" per la firma
        date = datetime.strptime(on, "%Y-%m-%d")
    except Exception as e:
        raise HTTPException(400, "Data non valida")

    claims = Auth().authenticate(authorization, fingerprint, claims=True)
    return sign_data(claims["uid"], data, on)


@router.post("/verify_signature")
async def verify(
    data: Annotated[DataWithSignature, Body(description="I dati firmati")],
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    """i dati devono contenere almeno una proprietà signature"""
    claims = Auth().authenticate(authorization, fingerprint, claims=True)
    return verify_signature(data)
