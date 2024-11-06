from typing import Annotated
from fastapi import Header, HTTPException, Cookie
import httpx
from ..endpoints import AUTHENTICATION_URL, CA_CERT_PATH


async def authentication_request(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> dict:
    """Request to the authentication service to get the claims of the user"""

    try:
        async with httpx.AsyncClient(verify=CA_CERT_PATH) as client:
            response = await client.get(
                AUTHENTICATION_URL,
                headers={"Authorization": authorization},
                cookies={"fingerprint": fingerprint},
                params={"claims": "true"},
            )
            if response.status_code != 200:
                raise HTTPException(response.status_code, response.headers["x-error"])
            return response.json()

    # deal with connection errors
    except httpx.ConnectError as e:
        raise HTTPException(500, "Errore di connessione con Auth Server")

    # deal with timout errors
    except httpx.TimeoutException as e:
        raise HTTPException(504, "Timeout: il server non risponde")

    # deal wiht HTTP errors
    except httpx.HTTPStatusError as e:
        raise HTTPException(500, "HTTPX: Errore HTTP")

    # deal with Auth Errors from remote auth service
    except Exception as e:
        raise HTTPException(e.status_code, e.detail)
