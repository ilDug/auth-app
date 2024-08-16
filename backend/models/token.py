from datetime import datetime
from pydantic import EmailStr
from .mongo import MongoModel


class JWTModel(MongoModel):
    nbf: datetime
    iat: datetime
    exp: datetime
    jti: str
    fingerprint_hash: str


class JWTAuth(JWTModel):
    uid: str | None = None
    email: EmailStr
    active: bool
    authorizations: list[str]


class JWTRefresh(JWTModel):
    passcode: str


class AccountAccessModel(MongoModel):
    uid: str
    jti: str
    date: datetime = datetime.now()
    # passcode: str
