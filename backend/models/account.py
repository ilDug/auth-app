from core.config import ACTIVATION_KEY_LENGTH
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, List
from .mongo import MongoModel


class AccountModel(MongoModel):
    """classe che definisce le proprietà  minime di un account utente"""

    uid: str
    username: str | None = None
    email: EmailStr
    active: bool = False
    authorizations: List[str] = []
    hashed_password: str | None = None
    registration_date: datetime | None = None
    # username: str | None = None
    # _pj = {"hashed_password": 0, "registration_date": 0}


class AccountActionKeyModel(MongoModel):
    """definizione della chiava usata per autorizzare le operazioni remote di un account"""

    uid: str
    key: Annotated[
        str,
        Field(..., min_length=ACTIVATION_KEY_LENGTH, max_length=ACTIVATION_KEY_LENGTH),
    ]
    created_at: datetime
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
