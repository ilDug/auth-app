from typing import Annotated
from fastapi import Cookie, APIRouter, Header, Query
from controllers.auth import Auth, TokenClaims


router = APIRouter(tags=["auth"], prefix="/api/auth/v2/auth")

# #########################################
# from icecream import ic

# ic.configureOutput(includeContext=True)
# #########################################


@router.get("/authenticate")
async def authenticate(
    claims: TokenClaims,
    with_claims: Annotated[
        bool | None,
        Query(description="Se True, restituisce i claims del token", alias="claims"),
    ] = False,
):

    return claims if with_claims else True


@router.get("/authorize")
async def authorization_check(
    claims: TokenClaims,
    permission: Annotated[
        str, Query(description="il permesso o il ruolo da verificare")
    ] = None,
):
    # se non c'è il permesso nei parametri della richiesta, non autorizza
    if permission is None:
        return False

    return permission in claims.get("authorizations", [])
