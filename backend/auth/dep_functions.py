from typing import Annotated, Callable
from fastapi import Cookie, Header
from .auth import Auth


async def authentication_guard(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> bool:

    auth = Auth()
    claims = auth.authenticate(authorization, fingerprint, claims=True)
    return claims is not None


async def is_admin(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> bool:

    auth = Auth()
    return auth.authorize(authorization, fingerprint, "admin")


async def authorization_fn(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> Callable:

    async def authorize_fn(permission: str):
        auth = Auth()
        return auth.authorize(authorization, fingerprint, permission)

    return authorize_fn
