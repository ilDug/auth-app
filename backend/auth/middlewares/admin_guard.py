from typing import Annotated
from fastapi import Header, HTTPException, Cookie
from .. import Auth


# verifica che sia un admin altrimenti blocca
async def admin_guard(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    try:
        return Auth().authorize(authorization, fingerprint, "admin")
    except Exception as e:
        raise HTTPException(401, str(e))
