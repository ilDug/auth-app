from typing import Annotated, Optional
from pydantic.networks import EmailStr
from fastapi import APIRouter, Body, Path, Response
from core.config import FINGERPRINT_COOKIE_LIFE
from ..models import RegisterRequestModel, LoginRequestModel, PasswordRestoreKeychain
from ..controllers import Account, AccountActivation, Password


router = APIRouter(tags=["account"])

cookies_setting = {
    "secure": True,
    "httponly": True,
    "samesite": "lax",
    "expires": FINGERPRINT_COOKIE_LIFE,
}


@router.post("/account/login")
async def login(res: Response, user: Annotated[LoginRequestModel, Body(...)]):
    token, fingerprint = Account.login(**user.model_dump())
    res.set_cookie("fingerprint", fingerprint, **cookies_setting)
    return token


@router.post("/account/register")
async def register(res: Response, user: Annotated[RegisterRequestModel, Body(...)]):
    token, fingerprint = Account.register(**user.model_dump())
    res.set_cookie("fingerprint", fingerprint, **cookies_setting)
    return token


@router.get("/account/activate/{key}")
async def activate(key: str):
    account = AccountActivation()
    return account.activate(key)


@router.get("/account/resend-activation/{email_md5_hash}")
async def resend(
    email_md5_hash: Annotated[str, Path(..., min_length=32, max_length=32)]
):
    account = AccountActivation()
    return account.resend_activation_email(email_md5_hash)


@router.get("/account/exists/{email_md5_hash}")
async def user_exists(email_md5_hash: Annotated[str, Path(...)]):
    account = Account()
    return account.exists(email_md5_hash)


@router.post(
    "/account/password/recover",
    description="genera una chiave di attivazione che permette di ripristinare la password",
)
async def password_recover(email: Annotated[dict, Body(...)]):
    pw = Password()
    return pw.recover(email["email"])


@router.get(
    "/account/password/restore/init/{key}",
    description="esegue i controlli per la reimpostazione della password utente",
)
async def password_restore_init(key: Annotated[str, Path(...)]):
    pw = Password()
    return pw.restore_init(key)


@router.post("/account/password/restore/set", description="imposta la nuova password")
async def password_restore_set(keychain: Annotated[PasswordRestoreKeychain, Body()]):
    pw = Password()
    return pw.restore_set(keychain.key, keychain.newpassword)