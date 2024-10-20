from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException
from pymongo import MongoClient
from core.config import MONGO_CS, DB
from models import UserKeyChain


def generate_crypto_keys() -> UserKeyChain:
    """genera la coppia di chiavi crittografiche"""

    # generate the private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # generate the public key
    public_key = private_key.public_key()

    # serialize the private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # serialize the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # return the keys as strings
    return UserKeyChain(
        private_key=private_pem.decode(),
        public_key=public_pem.decode(),
    )


def save_keys(uid: str, keychain: UserKeyChain):
    """salva la coppia di chiavi cryptografiche  nell'account utente"""

    # ritrova l'utente dal database in base al uid
    with MongoClient(MONGO_CS) as c:
        user = c[DB].accounts.find_one({"uid": uid})
        if user is None:
            raise HTTPException(404, "utente non trovato")

        # aggiorna l'utente con la nuova coppia di chiavi
        cursor = c[DB].accounts.update_one(
            {"uid": uid},
            {"$set": {"keychain": keychain.model_dump()}},
        )

        if cursor.modified_count < 1:
            raise HTTPException(500, "errore salvataggio chiavi")
