from datetime import datetime
import hashlib
from fastapi import HTTPException
from pymongo import MongoClient
from core.config import MONGO_CS, DB
from models import AccountModel, SignModel
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


async def sign_data(uid: str, data: str | dict) -> SignModel:
    """
    Signs the provided data using the private key associated with the given user ID.

    Args:
        uid (str): The unique identifier of the user.
        data (str | dict): The data to be signed. Can be a string or a dictionary.

    Returns:
        SignModel: An object containing the user ID, the current date, the signature, and the fingerprint of the data.

    Raises:
        HTTPException: If the user is not found in the database.

    """
    # ritrova l'utente dal database in base al uid
    user = await fetch_account(uid)

    # carica la chiave privata dell'utente
    private_key = serialization.load_pem_private_key(
        user.keychain.private_key.encode(),
        password=None,
    )

    # trasforma i dati in stringa se sono un dizionario
    data = str(data) if isinstance(data, dict) else data

    # calcola l'impronta dei dati
    data_hash = hashlib.sha256(data.encode()).hexdigest()

    # firma l'hash dei dati
    signature = private_key.sign(
        data_hash.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    # return the signature
    return SignModel(
        uid=uid,
        date=datetime.now(),
        sign=signature.hex(),
        fingerprint=data_hash,
    )


async def verify_signature(uid: str, signature: SignModel, data: str | dict):
    """
    Verifies the signature of the provided data using the public key associated with the given user ID.

    Args:
        signature (str): The signature to be verified.
        data (str | dict): The signed data. Can be a string or a dictionary.

    Returns:
        bool: True if the signature is valid, False otherwise.

    Raises:
        HTTPException: If the user is not found in the database.

    """
    # ritrova l'utente dal database in base al uid
    user = await fetch_account(uid)

    # carica la chiave pubblica dell'utente
    public_key = serialization.load_pem_public_key(
        user.keychain.public_key.encode(),
    )

    # trasforma i dati in stringa se sono un dizionario
    data = str(data) if isinstance(data, dict) else data

    # calcola l'impronta dei dati
    data_hash = hashlib.sha256(data.encode()).hexdigest()

    # se il fingerprint non corrisponde all'hash dei dati
    if data_hash != signature.fingerprint:
        raise HTTPException(400, "fingerprint non corrisponde")

    # verifica la firma
    try:
        public_key.verify(
            bytes.fromhex(signature.sign),
            data_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except Exception as e:
        raise HTTPException(400, "firma non valida")

    return True


async def fetch_account(uid):
    with MongoClient(MONGO_CS) as c:
        user = c[DB].accounts.find_one({"uid": uid})
        if user is None:
            raise HTTPException(404, "utente non trovato")

        user = AccountModel(**user)

        if user.keychain is None:
            raise HTTPException(404, "chiavi non trovate")
    return user
