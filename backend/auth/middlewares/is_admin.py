from typing import Annotated
from fastapi import Header, Cookie
from .. import Auth


# restituisce lo stato di admin
async def is_admin(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    try:
        return Auth().authorize(authorization, fingerprint, "admin")
    except Exception as e:
        return False
