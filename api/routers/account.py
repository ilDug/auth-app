from typing import Annotated
from fastapi import APIRouter, Body, Path, Query, Response
from core.config import COOKIES_SETTINGS
from models import AccessRequestModel, AccountRegistrationModel
from controllers.account import Account

router = APIRouter(tags=["account"], prefix="/api/v2/account")


@router.post("/account/login")
async def login(res: Response, user: Annotated[AccessRequestModel, Body(...)]):
    token, fingerprint = await Account().login(user.email, user.password)
    res.set_cookie("fingerprint", fingerprint, **COOKIES_SETTINGS)
    return token


@router.post("/register")
async def register(
    res: Response,
    user: Annotated[AccountRegistrationModel, Body(...)],
    notify: Annotated[bool, Query()] = True,
):
    token, fingerprint = await Account().register(user, notify=notify)
    res.set_cookie("fingerprint", fingerprint, **COOKIES_SETTINGS)
    return token


@router.get("/exists/{email_md5_hash}")
async def user_exists(email_md5_hash: Annotated[str, Path(...)]):
    return await Account().exists(email_md5_hash)


# @router.get("/activate/{key}")
# async def activate(key: str):
#     return await AccountActivation().activate(key)


# @router.get("/resend-activation/{email_md5_hash}")
# async def resend(
#     email_md5_hash: Annotated[str, Path(..., min_length=32, max_length=32)],
# ):
#     return await AccountActivation().resend_activation_email(email_md5_hash)


# @router.post(
#     "/password/recover",
#     description="genera una chiave di attivazione che permette di ripristinare la password",
# )
# async def password_recover(email: Annotated[dict, Body(...)]):
#     return await Password().recover(email["email"])


# @router.get(
#     "/password/restore/init/{key}",
#     description="esegue i controlli per la reimpostazione della password utente",
# )
# async def password_restore_init(key: Annotated[str, Path(...)]):
#     return Password().restore_init(key)


# @router.post("/password/restore/set", description="imposta la nuova password")
# async def password_restore_set(keychain: Annotated[PasswordRestoreKeychain, Body()]):
#     return Password().restore_set(keychain.key, keychain.newpassword)
