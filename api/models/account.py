import hashlib
import uuid
import bcrypt
from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)
from pydantic.alias_generators import to_camel
from typing import Annotated, List

from core.config import ACTIVATION_KEY_LENGTH, USER_NAMESPACE
from .sign import UserKeyChain
from .mongo import MongoBase
from .uuid_str import UuidStr
from controllers.account import generate_crypto_keys


class AccountModel(MongoBase):
    """classe che definisce le proprietà  minime di un account utente"""

    uid: UuidStr
    username: str | None = None
    email: EmailStr
    active: bool = False
    authorizations: List[str] = []
    password_hash: SecretStr | None = None
    registration_date: datetime | None = None
    keychain: UserKeyChain | None = None

    def to_public(self, include_id: bool = False) -> dict:
        """restituisce una rappresentazione pubblica dell'account senza dati sensibili"""
        allowed_fields = {
            "uid",
            "username",
            "email",
            "active",
            "authorizations",
            "registration_date",
        }
        if include_id:
            allowed_fields.add("id")
        return self.model_dump(include=allowed_fields)


class AccountRegistrationModel(BaseModel):
    """modello di registrazione di un nuovo account utente"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_name=True,
        validate_by_alias=True,
    )

    email: Annotated[EmailStr, Field(..., title="Email utente")]
    email_hash: Annotated[
        str | None,
        Field(title="Hash MD5 dell'email utente", exclude=True),
    ] = None
    password: Annotated[SecretStr, Field(title="Password dell'account", exclude=True)]
    password_hash: Annotated[
        str | None,
        Field(None, title="Hash SHA256 della password dell'account"),
    ] = None
    uid: UuidStr | None = None
    username: Annotated[
        str | None,
        Field(None, title="default username is the email without the domain part"),
    ] = None
    active: Annotated[
        bool,
        Field(title="indica se l'account è attivo"),
    ] = False
    authorizations: Annotated[
        List[str],
        Field(title="autorizzazioni e permessi dell'account"),
    ] = ["basic"]
    registration_date: Annotated[
        datetime | None, Field(title="data di registrazione dell'account")
    ] = datetime.now()
    keychain: Annotated[
        UserKeyChain | None,
        Field(title="coppia di chiavi crittografiche dell'utente"),
    ] = generate_crypto_keys()

    @field_validator("email", mode="before")
    def normalize_email(cls, value: str) -> str:
        return value.lower().strip()

    @field_validator("email_hash", mode="before")
    def compute_email_hash(cls, value: str | None) -> str:
        if cls.email is not None:
            return hashlib.md5(cls.email.encode()).hexdigest()
        else:
            return value

    @field_validator("password_hash", mode="before")
    def compute_password_hash(cls, value: str | None) -> str:
        if cls.password is not None:
            return bcrypt.hashpw(
                cls.password.get_secret_value().encode(), bcrypt.gensalt()
            ).decode()
        else:
            return value

    @field_validator("uid", mode="before")
    def compute_uid(cls, value: UuidStr | None) -> UuidStr:
        if cls.email is not None:
            return UuidStr.from_uuid(uuid.uuid5(USER_NAMESPACE, cls.email))
        else:
            return value

    @field_validator("username", mode="before")
    def compute_username(cls, value: str | None) -> str | None:
        if value is None and cls.email is not None:
            return cls.email.split("@")[0]
        else:
            return value


class AccountActionKeyModel(MongoBase):
    """definizione della chiava usata per autorizzare le operazioni remote di un account"""

    uid: str
    key: Annotated[
        str,
        Field(..., min_length=ACTIVATION_KEY_LENGTH, max_length=ACTIVATION_KEY_LENGTH),
    ]
    created_at: datetime = datetime.now()
    used_at: datetime | None = None
    scope: str


class AccessRequestModel(BaseModel):
    """modello di accesso all'account da parte di un utente, per LOGIN o il REGISTER"""

    email: Annotated[EmailStr, Field(..., title="Email utente")]
    password: Annotated[SecretStr, Field(..., title="Password dell'account")]

    @field_validator("email", mode="before")
    def normalize_email(cls, value: str) -> str:
        return value.lower().strip()


class PasswordRestoreKeychain(BaseModel):
    """dati necessari alla richietta di recupero password"""

    key: Annotated[
        str,
        Field(..., min_length=ACTIVATION_KEY_LENGTH, max_length=ACTIVATION_KEY_LENGTH),
    ]
    newpassword: str


class LoginResponse(BaseModel):
    # dag access token (da salvare nel session storage)
    dat: Annotated[
        str, Field(title="dag access token (da salvare nel session storage)")
    ]

    drt: Annotated[
        str | None, Field(title="dag refresh token (da salvare nel local storage)")
    ] = None

    dfp: Annotated[
        str | None, Field(title="dag fingerprint (da salvare nei cookies)")
    ] = None
