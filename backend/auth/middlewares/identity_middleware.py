from typing import Annotated
from fastapi import Header, Cookie
from .. import Auth


async def identity_mdw(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    """DEPENDENCY che ritorna il uid dell'utente"""
    try:
        claims = Auth().authenticate(authorization, fingerprint, claims=True)
        uid = claims["uid"]
        return uid
    except Exception as e:
        return None
