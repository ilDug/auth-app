from pydantic import BaseModel, ConfigDict, EmailStr


class SignPayloadModel(BaseModel):
    """
    Oggetto che rappresenta il payload da firmare.

    il `payload` è il contenuto da firmare, in formato hexadecimale dei bytes del contenuto.
    """

    uid: str  # user id
    date: str  # date of sign formatted like yyyy-mm-dd
    payload: str  # data to sign


class SignModel(BaseModel):
    """contenuto della firma"""

    uid: str  # user id
    date: str  # date of sign formatted like yyyy-mm-dd
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
    date: str   # date of sign formatted like yyyy-mm-dd
    uid: str
    user: EmailStr
    fingerprint: str
    errors: list[str] = []
    msg: str
