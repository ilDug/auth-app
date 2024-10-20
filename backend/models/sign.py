from pydantic import BaseModel
from datetime import datetime


class SignModel(BaseModel):
    uid: str  # user id
    date: datetime = datetime.now()  # date of sign
    sign: str  # signature
    fingerpint: str  # hash of the file sha256


class UserKeyChain(BaseModel):
    public_key: str  # public key
    private_key: str  # private key
