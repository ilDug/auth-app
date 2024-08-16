from typing import Annotated
from fastapi import Header, HTTPException, Cookie
from .. import Auth


async def authentication_guard(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    try:
        return Auth().authenticate(authorization, fingerprint, claims=False)
    except Exception as e:
        raise HTTPException(401, str(e))
