from typing import Annotated, Callable
from fastapi import Depends
from .get_authorizations import authorization_request


async def is_admin(
    authorizeFn: Annotated[Callable, Depends(authorization_request)]
) -> bool:
    """Check if the user has the admin permission"""

    return await authorizeFn("admin")
