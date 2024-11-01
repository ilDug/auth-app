from typing import Annotated, Callable
from fastapi import Cookie, Header
from core.config import REGISTRATION_BEHAVIOUR
from .auth import Auth


async def authentication_guard(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> bool:
    """
    Asynchronous function to guard authentication.
    This function checks the provided authorization header and fingerprint cookie
    to authenticate a user and verify their claims.
    Args:
        authorization (Annotated[str | None, Header]): The authorization token from the request header.
        fingerprint (Annotated[str | None, Cookie]): The fingerprint token from the request cookie.
    Returns:
        bool: True if the claims are valid, False otherwise.
    """
    auth = Auth()
    claims = auth.authenticate(authorization, fingerprint, claims=True)
    return claims is not None


async def is_admin(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> bool:
    """
    Check if the user is an admin based on authorization and fingerprint.

    Args:
        authorization (Annotated[str | None, Header]): The authorization token from the request header.
        fingerprint (Annotated[str | None, Cookie]): The fingerprint from the request cookie.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """

    auth = Auth()
    return auth.authorize(authorization, fingerprint, "admin")


async def authorization_fn(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> Callable:
    """
    Asynchronous function to create an authorization function with provided headers and cookies.

    Args:
        authorization (Annotated[str | None, Header]): The authorization header, which can be None.
        fingerprint (Annotated[str | None, Cookie]): The fingerprint cookie, which can be None.

    Returns:
        Callable: A function that takes a permission string and returns the result of the authorization check.
    """

    async def authorize_fn(permission: str):
        auth = Auth()
        # prima prova a vedere se è admin (ACCESSO COMPLETO A TUTTO)
        try:
            is_admin = auth.authorize(authorization, fingerprint, "admin")
        except Exception:
            is_admin = False
        finally:
            return (
                True
                if is_admin
                else auth.authorize(authorization, fingerprint, permission)
            )

    return authorize_fn


async def registration_behaviour(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> bool:
    match REGISTRATION_BEHAVIOUR:
        case "ALLOW_ANYBODY":
            return True
        case "ONLY_ADMIN":
            return await is_admin(authorization, fingerprint)
        case _:
            return True


async def get_token_claims(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> dict:
    """
    Get the claims from the token.
    """

    auth = Auth()
    return auth.authenticate(authorization, fingerprint, claims=True)


async def get_uid(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> str:
    """
    Get the uid from the token.
    """

    auth = Auth()
    claims = auth.authenticate(authorization, fingerprint, claims=True)
    return claims["uid"]


async def get_email(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> str:
    """
    Get the email from the token.
    """

    auth = Auth()
    claims = auth.authenticate(authorization, fingerprint, claims=True)
    return claims["email"]
