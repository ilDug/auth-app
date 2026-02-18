from typing import Annotated
from fastapi import (
    APIRouter,
    Body,
    Cookie,
    HTTPException,
    Header,
    Path,
    Query,
    Response,
)
from core.config import ACTIVATION_KEY_LENGTH, COOKIES_SETTINGS, REGISTRATION_BEHAVIOUR
from models import AccessRequestModel, AccountRegistrationModel, PasswordRestoreKeychain
from controllers.account import Account, AccountActivation, Password
from controllers.auth import get_token_claims
from pydantic import EmailStr

router = APIRouter(tags=["account"], prefix="/account")


@router.post("/login")
async def login(res: Response, user: Annotated[AccessRequestModel, Body(...)]):
    token, fingerprint = await Account().login(user.email, user.password)
    res.set_cookie("fingerprint", fingerprint, **COOKIES_SETTINGS)
    return token


@router.post("/register")
async def register(
    res: Response,
    user: Annotated[AccountRegistrationModel, Body(...)],
    notify: Annotated[bool, Query()] = True,
    authorization: Annotated[str | None, Header()] = None,
    fingerprint: Annotated[str | None, Cookie()] = None,
):

    match REGISTRATION_BEHAVIOUR:
        case "ALLOW_ANYBODY":
            # se è permesso a chiunque di registrarsi, restituisco direttamente il token di accesso
            token, fp = await Account().register(user, notify=notify)
            res.set_cookie("fingerprint", fp, **COOKIES_SETTINGS)
            return token

        case "ONLY_ADMIN":
            # se solo gli admin possono registrare nuovi utenti, restituisco un messaggio di successo generico
            claims = get_token_claims(authorization, fingerprint)
            permissions = claims.get("authorizations", [])
            if "admin" not in permissions:
                raise HTTPException(
                    status_code=403,
                    detail="only admins can register new users",
                )

            token, fp = await Account().register(user, notify=notify)
            return {"message": f"user {user.email} registered successfully"}

        case _:
            raise ValueError("invalid registration behaviour setted in Env variables")


@router.get("/exists/{email_md5_hash}")
async def user_exists(email_md5_hash: Annotated[str, Path(...)]):
    return await Account().exists(email_md5_hash)


@router.get("/activate/{key}")
async def activate(key: str):
    return await AccountActivation().activate(key)


@router.get("/resend-activation/{email_md5_hash}")
async def resend(
    email_md5_hash: Annotated[str, Path(..., min_length=32, max_length=32)],
):
    return await AccountActivation().resend_activation_email(email_md5_hash)


@router.post(
    "/password/recover",
    description="genera una chiave di attivazione che permette di ripristinare la password",
)
async def password_recover(email: Annotated[EmailStr, Body(...)]):
    return await Password().recover(email)


@router.get(
    "/password/restore/init/{key}",
    description="esegue i controlli per la reimpostazione della password utente",
)
async def password_restore_init(
    key: Annotated[
        str,
        Path(..., min_length=ACTIVATION_KEY_LENGTH, max_length=ACTIVATION_KEY_LENGTH),
    ],
):
    return await Password().restore_init(key)


@router.post("/password/restore/set", description="imposta la nuova password")
async def password_restore_set(keychain: Annotated[PasswordRestoreKeychain, Body()]):
    return await Password().restore_set(keychain.key, keychain.newpassword)
