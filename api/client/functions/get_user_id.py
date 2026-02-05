from typing import Annotated
from fastapi import Cookie, Header
from .get_claims import authentication_request


async def get_user_id(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> str:
    """Get the user id from the claims"""

    claims = await authentication_request(authorization, fingerprint)
    return claims["uid"]
