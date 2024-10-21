from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class SignPayloadModel(BaseModel):
    """Oggetto che rappresenta il payload da firmare"""

    uid: str  # user id
    date: datetime = datetime.now()  # date of sign
    payload: str


class SignModel(BaseModel):
    """contenuto della firma"""

    uid: str  # user id
    date: datetime  # date of sign
    fingerprint: str  # hash of the file sha256
    signature: str  # signature


class UserKeyChain(BaseModel):
    """coppia di chiavi"""

    public_key: str  # public key
    private_key: str  # private key


class DataWithSignature(BaseModel):
    """qualsiasi tipo di dati a cui si aggiunge la proprietà signature. Necessari a verificare la firma"""

    signature: SignModel

    model_config = ConfigDict(
        extra="allow",
    )


class SignVerifyReport(BaseModel):
    """report di verifica della firma digitale"""

    verified: bool
    date: datetime
    uid: str
    user: EmailStr
    fingerprint: str
    errors: list[str] = []
    msg: str
