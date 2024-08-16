from typing import Annotated
from fastapi.param_functions import Path
from fastapi import Cookie, APIRouter, Header
from core.auth import Auth

router = APIRouter(tags=["auth"])


@router.get("/auth/authorization/check/permission/{permission}")
async def authorization_check(
    permission: Annotated[str, Path()],
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    return Auth().authorize(authorization, fingerprint, permission)
