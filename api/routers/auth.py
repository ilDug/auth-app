from typing import Annotated
from fastapi import Cookie, APIRouter, Header, Query
from controllers.auth import Auth

router = APIRouter(tags=["auth"], prefix="/api/auth/v2/auth")

# #########################################
# from icecream import ic

# ic.configureOutput(includeContext=True)
# #########################################


@router.get("/authenticate")
async def authenticate(
    authorization: Annotated[str | None, Header()] = None,
    claims: Annotated[
        bool | None, Query(description="Se True, restituisce i claims del token")
    ] = False,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    claims = Auth().authenticate(authorization, fingerprint, claims=claims)
    return claims


@router.get("/authorize")
async def authorization_check(
    authorization: Annotated[str | None, Header()] = None,
    permission: Annotated[
        str, Query(description="il permesso o il ruolo da verificare")
    ] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    # se non c'è il permesso nei parametri della richiesta, non autorizza
    if permission is None:
        return False

    auth = Auth()
    # prima prova a vedere se è admin (ACCESSO COMPLETO A TUTTO)
    try:
        is_admin = auth.authorize(authorization, fingerprint, "admin")
    except Exception:
        is_admin = False
    finally:
        return (
            True if is_admin else auth.authorize(authorization, fingerprint, permission)
        )
