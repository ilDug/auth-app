import hashlib
import uuid
import bcrypt
from datetime import datetime
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)
from typing import Annotated, List

from core.config import ACTIVATION_KEY_LENGTH, USER_NAMESPACE
from core.utils import generate_crypto_keys, UserKeyChain
from .mongo import MongoBase
from .uuid_str import UuidStr


class AccountModel(MongoBase):
    """classe che definisce le proprietà  minime di un account utente"""

    uid: Annotated[UuidStr, Field(None, title="UUIDv5 dell'account utente")]
    username: Annotated[
        str,
        Field(None, title="default username is the email without the domain part"),
    ]
    email: Annotated[EmailStr, Field(..., title="Email utente")]
    active: Annotated[
        bool,
        Field(title="indica se l'account è attivo"),
    ] = False
    authorizations: Annotated[
        List[str],
        Field(title="autorizzazioni e permessi dell'account"),
    ] = []
    password_hash: Annotated[
        str, Field(None, title="Hash SHA256 della password dell'account")
    ]
    registration_date: Annotated[
        datetime, Field(title="data di registrazione dell'account")
    ] = datetime.now()
    keychain: Annotated[
        UserKeyChain, Field(title="coppia di chiavi crittografiche dell'utente")
    ]

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


class AccountRegistrationModel(AccountModel):
    """modello di registrazione di un nuovo account utente"""

    email_hash: Annotated[
        str,
        Field(None, title="Hash MD5 dell'email utente", exclude=True),
    ]
    password: Annotated[
        SecretStr, Field(title="Password dell'account", exclude=True, min_length=8)
    ]

    @model_validator(mode="before")
    def initialize_account_fields(cls, data: dict) -> dict:
        """Calcola i campi derivati da email e password"""

        if isinstance(data, dict):
            # Normalizza email prima di usarla
            if "email" in data:
                email = data["email"].lower().strip()
                data["email"] = email

                # Calcola email_hash se non presente
                if "email_hash" not in data or data["email_hash"] is None:
                    data["email_hash"] = hashlib.md5(email.encode()).hexdigest()

                # Calcola uid se non presente
                if "uid" not in data or data["uid"] is None:
                    data["uid"] = str(uuid.uuid5(USER_NAMESPACE, email))

                # Calcola username se non presente
                if "username" not in data or data["username"] is None:
                    data["username"] = email.split("@")[0]

            # Calcola password_hash se password è presente
            if "password" in data and data["password"] is not None:
                if "password_hash" not in data or data["password_hash"] is None:
                    # Gestisci sia SecretStr che string
                    pwd: str = (
                        data["password"].get_secret_value()
                        if hasattr(data["password"], "get_secret_value")
                        else data["password"]
                    )
                    data["password_hash"] = bcrypt.hashpw(
                        pwd.encode(), bcrypt.gensalt()
                    ).decode()

            if "keychain" not in data or data["keychain"] is None:
                data["keychain"] = generate_crypto_keys()

        return data


class AccountActionKeyModel(MongoBase):
    """definizione della chiava usata per autorizzare le operazioni remote di un account"""

    uid: UuidStr
    key: Annotated[
        str,
        Field(..., min_length=ACTIVATION_KEY_LENGTH, max_length=ACTIVATION_KEY_LENGTH),
    ]
    created_at: datetime | None = datetime.now()
    used_at: datetime | None = None
    scope: str


class AccessRequestModel(BaseModel):
    """modello di accesso all'account da parte di un utente, per LOGIN o il REGISTER"""

    email: Annotated[EmailStr, Field(..., title="Email utente")]
    password: Annotated[
        SecretStr,
        Field(..., title="Password dell'account", min_length=8),
    ]

    @field_validator("email", mode="before")
    def normalize_email(cls, value: str) -> str:
        return value.lower().strip()


class PasswordRestoreKeychain(BaseModel):
    """dati necessari alla richietta di recupero password"""

    key: Annotated[
        str,
        Field(..., min_length=ACTIVATION_KEY_LENGTH, max_length=ACTIVATION_KEY_LENGTH),
    ]
    newpassword: Annotated[SecretStr, Field(..., title="Nuova password")]


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
