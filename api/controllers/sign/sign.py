from datetime import datetime
import hashlib
import pickle
from fastapi import HTTPException
from models import (
    AccountModel,
    SignModel,
    SignPayloadModel,
    DataWithSignature,
    SignVerifyReport,
)
from controllers.account import Account
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


##########################################################
def generate_signature(
    data: str | dict | int | float,
    user: AccountModel,
    date: str,
) -> SignModel:
    """
    Signs the provided data using the private key associated with the given user ID.

    Args:
        user (AccountModel): The authenticated user object containing user details and keychain.
        data (str | dict | int | float): The data to be signed. Can be a string, dictionary, integer, or float.
        date (str): The date of signing. Formatted like "yyy-mm-dd".

    Returns:
        SignModel: An object containing the user ID, the current date, the signature, and the fingerprint of the data.
    """
    # carica la chiave privata dell'utente
    private_key = serialization.load_pem_private_key(
        user.keychain.private_key.encode(),
        password=None,
    )

    # rimuove la firma dai dati (se esiste)
    if isinstance(data, dict) and "signature" in data:
        data.pop("signature")

    data_hex, data_hash = digest_data_for_signature(data)

    # genera il payload da firmare
    payload = SignPayloadModel(
        uid=user.uid,
        date=date,
        payload=data_hex,
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
        uid=user.uid,
        date=payload.date,
        fingerprint=data_hash,
        signature=signature.hex(),
    )


async def verify_signature(data: DataWithSignature) -> SignVerifyReport:
    """
    Verifies the signature of the provided data using the public key associated with the given user ID.

    Args:
        data (DataWithSignature): An object containing the signed data and the signature.

    Returns:
        SignVerifyReport: An object containing the verification result and additional information.
    """
    # estrae i dati della firma dal payload
    signature = data.signature  # SignModel

    # ritrova l'utente dal database in base al uid
    user = await Account.get_user(uid=signature.uid)

    # carica la chiave pubblica dell'utente
    public_key = serialization.load_pem_public_key(
        user.keychain.public_key.encode(),
    )

    # estrae tutti  i dati  tranne la firma dal payload
    data_raw = data.model_dump(exclude={"signature"})

    # calcola l'impronta dei dati
    data_hex, data_hash = digest_data_for_signature(data_raw)

    # trasforma la firma in byte
    signature_bytes = bytes.fromhex(signature.signature)

    # genera il payload da verificare
    payload = SignPayloadModel(
        uid=signature.uid,
        date=signature.date,
        payload=data_hex,
    )
    payload_bytes = payload.model_dump_json().encode()

    ######## VERIFICHE ########
    errors = []

    # se il fingerprint non corrisponde all'hash dei dati
    if data_hash != signature.fingerprint:
        errors.append("fingerprint non corrispondente")

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
    except InvalidSignature:
        errors.append("data or signature not authentic")

    verified = len(errors) == 0

    return SignVerifyReport(
        verified=verified,
        date=payload.date,
        uid=payload.uid,
        user=user.email,
        fingerprint=data_hash,
        errors=errors,
        msg=(
            f"Document correctly signed by {user.email} on {datetime.strptime(payload.date, '%Y-%m-%d').strftime('%d/%m/%Y')}"
            if verified
            else f"Errors in signature verification: {'; '.join(errors)}"
        ),
    )


##########################################################
# Helper Functions
##########################################################


def digest_data_for_signature(data: str | dict | int | float) -> tuple[str, str]:
    """
    Transforms the input data into bytes and computes its SHA-256 hash.

    Args:
        data (str | dict | int | float): The input data to be transformed and hashed. It can be of any type (str, dict, int, float, etc.).

    Returns:
        tuple: A tuple containing the hex representation of the byte of the input data and its SHA-256 hash as a hexadecimal string.
    """

    # transforms the parameter `data` into bytes.
    # please note that data can be an instance
    # of any type : str, dict, int, float, etc.
    match data:
        case str() | int() | float():
            data_bytes = str(data).encode()

        case dict():
            data_bytes = pickle.dumps(data)

        case _:
            raise HTTPException(400, "Tipo di dato non supportato per la firma")

    # converte i bytes in una stringa esadecimale
    data_hex = data_bytes.hex()

    # calcola l'impronta dei dati
    data_hash = hashlib.sha256(data_bytes).hexdigest()

    return data_hex, data_hash
