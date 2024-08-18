from typing import Annotated
from fastapi import Depends
from .get_claims import authentication_request


async def authentication_guard(
    claims: Annotated[dict, Depends(authentication_request)]
) -> bool:
    """Check if the user is authenticated"""

    return claims is not None
