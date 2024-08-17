from typing import Annotated, Callable
from fastapi import Header, HTTPException, Cookie, Depends, Query
import requests
import requests.exceptions
import httpx

AUTHENTICATION_URL = "http://backend:8000/auth/authenticate?claims=True"
AUTHORIZATION_URL = "http://backend:8000/auth/authorize"


async def authentication(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                AUTHENTICATION_URL,
                headers={"Authorization": authorization},
                cookies={"fingerprint": fingerprint},
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


async def user_id(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    claims = await authentication(authorization, fingerprint)
    return claims["uid"]


async def permissions(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
    claims = await authentication(authorization, fingerprint)
    return claims["authorizations"]


async def authorization(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):
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


async def is_admin(authorizeFn: Annotated[Callable, Depends(authorization)]):
    return await authorizeFn("admin")
