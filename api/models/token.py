from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from .mongo import MongoBase
from pydantic.alias_generators import to_camel


class JWTModel(BaseModel):
    model_config = ConfigDict(
        extra="allow", alias_generator=to_camel, serialize_by_alias=True
    )

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


class AccountAccessModel(MongoBase):
    uid: str
    jti: str
    date: datetime = datetime.now()
    # passcode: str
