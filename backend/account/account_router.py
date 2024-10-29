from typing import Annotated
from fastapi import APIRouter, Body, Depends, Path, Query, Response
from core.config import COOKIES_SETTINGS
from models import RegisterRequestModel, LoginRequestModel, PasswordRestoreKeychain
from .controllers import Account, AccountActivation, Password
from auth import registration_behaviour

router = APIRouter(tags=["account"])


@router.post("/account/login")
async def login(res: Response, user: Annotated[LoginRequestModel, Body(...)]):
    token, fingerprint = Account().login(**user.model_dump())
    res.set_cookie("fingerprint", fingerprint, **COOKIES_SETTINGS)
    return token


@router.post("/account/register", dependencies=[Depends(registration_behaviour)])
async def register(
    res: Response,
    user: Annotated[RegisterRequestModel, Body(...)],
    notify: Annotated[bool, Query()] = True,
):
    token, fingerprint = Account().register(**user.model_dump())
    res.set_cookie("fingerprint", fingerprint, **COOKIES_SETTINGS)
    return token


@router.get("/account/exists/{email_md5_hash}")
async def user_exists(email_md5_hash: Annotated[str, Path(...)]):
    return Account().exists(email_md5_hash)


@router.get("/account/activate/{key}")
async def activate(key: str):
    return AccountActivation().activate(key)


@router.get("/account/resend-activation/{email_md5_hash}")
async def resend(
    email_md5_hash: Annotated[str, Path(..., min_length=32, max_length=32)]
):
    return AccountActivation().resend_activation_email(email_md5_hash)


@router.post(
    "/account/password/recover",
    description="genera una chiave di attivazione che permette di ripristinare la password",
)
async def password_recover(email: Annotated[dict, Body(...)]):
    return Password().recover(email["email"])


@router.get(
    "/account/password/restore/init/{key}",
    description="esegue i controlli per la reimpostazione della password utente",
)
async def password_restore_init(key: Annotated[str, Path(...)]):
    return Password().restore_init(key)


@router.post("/account/password/restore/set", description="imposta la nuova password")
async def password_restore_set(keychain: Annotated[PasswordRestoreKeychain, Body()]):
    return Password().restore_set(keychain.key, keychain.newpassword)


# @router.get("/account/add_keys_to_all_accounts")
# async def generate_keys():
#     add_keys_to_all_accounts()
#     return True
