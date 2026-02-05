from typing import Annotated, Callable
from fastapi import Cookie, Depends, Header
from .auth import Auth
from ..account import Account


def authentication_guard(
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


def is_admin(
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


def get_token_claims(
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
) -> dict:
    """
    Get the claims from the token.
    """

    auth = Auth()
    return auth.authenticate(authorization, fingerprint, claims=True)


async def get_uid(claims: Annotated[dict, Depends(get_token_claims)]) -> str:
    """
    Get the uid from the token.
    """
    return claims["uid"]


async def get_email(claims: Annotated[dict, Depends(get_token_claims)]) -> str:
    """
    Get the email from the token.
    """
    return claims["email"]


async def get_account(uid: Annotated[str, Depends(get_uid)]) -> Account:
    """
    Get the authenticated account.
    """
    account = await Account.get_user(uid=uid)
    return account


async def get_permissions(
    claims: Annotated[dict, Depends(get_token_claims)],
) -> list[str]:
    """
    Get the permissions from the token claims.
    """
    return claims.get("authorizations", [])
