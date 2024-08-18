from typing import Annotated, Callable
from fastapi import Header, HTTPException, Cookie
import requests.exceptions
import httpx
from ..endpoints import AUTHORIZATION_URL


async def authorization_request(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> Callable:
    """Request to the authorization service to check if the user has the permission, and return a function to check the permission"""

    async def authorizeFn(permission: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    AUTHORIZATION_URL,
                    headers={"Authorization": authorization},
                    cookies={"fingerprint": fingerprint},
                    params={"permission": permission},
                )
                if response.status_code != 200:
                    raise HTTPException(
                        response.status_code, response.headers["x-error"]
                    )
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

    return authorizeFn
