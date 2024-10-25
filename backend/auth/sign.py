from datetime import datetime
import hashlib
from fastapi import HTTPException
from pymongo import MongoClient
from core.config import MONGO_CS, DB
from models import (
    AccountModel,
    SignModel,
    SignPayloadModel,
    DataWithSignature,
    SignVerifyReport,
)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


##########################################################
def sign_data(uid: str, data: str | dict, date: datetime = datetime.now()) -> SignModel:
    """
    Signs the provided data using the private key associated with the given user ID.

    Args:
        uid (str): The unique identifier of the user.
        data (str | dict): The data to be signed. Can be a string or a dictionary.

    Returns:
        SignModel: An object containing the user ID, the current date, the signature, and the fingerprint of the data.
    """
    # ritrova l'utente dal database in base al uid
    user = fetch_account(uid)

    # carica la chiave privata dell'utente
    private_key = serialization.load_pem_private_key(
        user.keychain.private_key.encode(),
        password=None,
    )

    data_str, data_hash = digest_data_for_signature(data)

    # genera il payload da firmare
    payload = SignPayloadModel(
        uid=uid,
        date=date,
        payload=data_str,
    )
    payload_bytes = payload.model_dump_json().encode()

    # firma il payload
    signature = private_key.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    # return the signature
    return SignModel(
        uid=uid,
        date=payload.date,
        fingerprint=data_hash,
        signature=signature.hex(),
    )


def verify_signature(uid: str, data: DataWithSignature) -> bool:
    """
    Verifies the signature of the provided data using the public key associated with the given user ID.

    Args:
        uid (str): The unique identifier of the user.
        data (DataWithSignature): An object containing the signed data and the signature.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    # ritrova l'utente dal database in base al uid
    user = fetch_account(uid)

    # carica la chiave pubblica dell'utente
    public_key = serialization.load_pem_public_key(
        user.keychain.public_key.encode(),
    )

    # estrae tutti  i dati  tranne la firma dal payload
    data_raw = data.model_dump(exclude={"signature"})

    # calcola l'impronta dei dati
    data_str, data_hash = digest_data_for_signature(data_raw)

    # estrae la firma dal payload
    signature = data.signature

    # trasforma la firma in byte
    signature_bytes = bytes.fromhex(signature.signature)

    # genera il payload da verificare
    payload = SignPayloadModel(
        uid=signature.uid,
        date=signature.date,
        payload=data_str,
    )
    payload_bytes = payload.model_dump_json().encode()

    ######## VERIFICHE ########
    errors = []

    # se il fingerprint non corrisponde all'hash dei dati
    if data_hash != signature.fingerprint:
        errors.append("fingerprint non corrispondente")

    # se l'utente non corrisponde
    if uid != signature.uid:
        errors.append("utente non corrispondente")

    try:
        # verifica la firma
        public_key.verify(
            signature_bytes,
            payload_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except InvalidSignature as e:
        errors.append("data o firma non autentiche")

    verified = len(errors) == 0

    return SignVerifyReport(
        verified=verified,
        date=payload.date,
        uid=payload.uid,
        user=user.email,
        fingerprint=data_hash,
        errors=errors,
        msg=(
            f"Documento firmato correttamente da {user.email} il {payload.date.strftime('%d/%m/%Y')}"
            if verified
            else f'Errori nella verifica della firma: {"; ".join(errors)}'
        ),
    )


##########################################################
# Helper Functions
##########################################################


def fetch_account(uid):
    with MongoClient(MONGO_CS) as c:
        user = c[DB].accounts.find_one({"uid": uid})
        if user is None:
            raise HTTPException(404, "utente non trovato")

        user = AccountModel(**user)

        if user.keychain is None:
            raise HTTPException(404, "chiavi non trovate")

        return user


def digest_data_for_signature(data):
    # trasforma i dati in stringa se sono un dizionario
    _string = str(data) if isinstance(data, dict) else data

    # trasforma i dati in byte
    _bytes = _string.encode()

    # calcola l'impronta dei dati
    _hash = hashlib.sha256(_bytes).hexdigest()

    return _string, _hash
