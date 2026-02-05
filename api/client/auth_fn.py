from typing import Annotated
from fastapi import Depends, Header, HTTPException, Cookie
import httpx
import logging
from .endpoints import AUTHENTICATION_URL, CA_CERT_PATH

logger = logging.getLogger(__name__)


async def authentication_request(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> dict:
    """Request to the authentication service to get the claims of the user"""

    if authorization is None or fingerprint is None:
        raise HTTPException(401, "Missing Authorization Header or Fingerprint")

    try:
        async with httpx.AsyncClient(verify=CA_CERT_PATH) as client:
            response = await client.get(
                AUTHENTICATION_URL,
                headers={"Authorization": authorization},
                cookies={"fingerprint": fingerprint},
                params={"claims": "true"},
            )
            if response.status_code != 200:
                raise HTTPException(
                    response.status_code,
                    response.headers.get("x-error", "Remote Authentication failed"),
                )
            return response.json()

    # Errori di connessione al server
    except httpx.ConnectError as e:
        logger.error(f"Connection error to auth server: {e}")
        raise HTTPException(503, "Errore di connessione con Auth Server")

    # Errori di timeout
    except httpx.TimeoutException as e:
        logger.error(f"Timeout connecting to auth server: {e}")
        raise HTTPException(504, "Timeout: il server non risponde")

    # Errori HTTP specifici
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from auth server: {e}")
        raise HTTPException(
            e.response.status_code, "Errore HTTP dal server di autenticazione"
        )

    # Errori HTTPException già sollevati (es: 401, o dal check status_code != 200)
    except HTTPException:
        raise

    # Altri errori imprevisti
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
        raise HTTPException(500, "Errore interno durante l'autenticazione")


async def auth_claims(claims: Annotated[dict, Depends(authentication_request)]) -> dict:
    """Funzione di utilità per ottenere le claims dell'utente autenticato"""

    # Ottieni le claims dell'utente autenticato
    return claims


async def get_user_id(claims: Annotated[dict, Depends(authentication_request)]) -> str:
    """Get the user id from the claims"""
    return claims.get("uid", None)


async def get_email(claims: Annotated[dict, Depends(authentication_request)]) -> str:
    """Get the email from the claims"""
    return claims.get("email", None)


async def get_permissions(claims: Annotated[dict, Depends(authentication_request)]):
    """Get the permissions from the claims"""

    return claims.get("authorizations", [])


async def is_authenticated(
    claims: Annotated[dict, Depends(authentication_request)],
) -> bool:
    """Check if the user is authenticated"""

    return claims is not None


async def is_admin(claims: Annotated[dict, Depends(authentication_request)]) -> bool:
    """Check if the user has admin permissions"""

    return "admin" in claims.get("authorizations", [])
