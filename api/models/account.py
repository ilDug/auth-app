from core.config import ACTIVATION_KEY_LENGTH
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, SecretStr
from typing import Annotated, List

from .sign import UserKeyChain
from .mongo import MongoBase
from .uuid_str import UuidStr


class AccountModel(MongoBase):
    """classe che definisce le proprietà  minime di un account utente"""

    uid: UuidStr
    username: str | None = None
    email: EmailStr
    active: bool = False
    authorizations: List[str] = []
    hashed_password: SecretStr | None = None
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


# Modello UTENTE in fase di login
class LoginRequestModel(BaseModel):
    """dati necessari alla richiesta di login"""

    # username: Annotated[str, Field(..., title="Nome utente")]
    email: Annotated[EmailStr, Field(..., title="Email utente")]
    password: Annotated[str, Field(..., title="Password dell'account")]


# modello UTENTE in fase di registrazione
class RegisterRequestModel(BaseModel):
    """dati necessari alla richiesta di registrazione account"""

    # username: Annotated[str, Field(..., title="Nome utente")]
    email: Annotated[EmailStr, Field(..., title="Email utente")]
    password: Annotated[str, Field(..., title="Password dell'account")]


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
