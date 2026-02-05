from typing import Annotated
from .get_claims import authentication_request
from fastapi import Cookie, Header


async def get_permissions(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> list:
    """Get the permissions from the claims"""

    claims = await authentication_request(authorization, fingerprint)
    return claims["authorizations"]
