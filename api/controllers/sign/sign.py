from datetime import datetime, timezone
import hashlib
import json
import base64
from typing import Any
from unittest import case
from fastapi import HTTPException
from models import AccountModel
from models.sign import (
    SignatureMetadata,
    DigitalSignature,
    SignedDocument,
    SignatureVerificationResult,
)
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

##########################################################
# FIRMA DIGITALE
##########################################################


def sign_content(content: Any, user: AccountModel, date: str) -> SignedDocument:
    """
    Firma digitalmente un contenuto usando la chiave privata dell'utente.

    Args:
        content: Contenuto da firmare (dict o str)
        user: Utente autenticato che firma
        date: Data della firma nel formato yyyy-mm-dd

    Returns:
        SignedDocument: Documento firmato con metadata

    Raises:
        HTTPException: Se il contenuto non è serializzabile o la firma fallisce
    """
    # 1. Carica la chiave privata dell'utente
    try:
        private_key = serialization.load_pem_private_key(
            user.keychain.private_key.encode(),
            password=None,
        )
    except Exception as e:
        raise HTTPException(500, f"Errore nel caricamento della chiave privata: {e}")

    # 2. Rimuove signature se già presente nel contenuto (per evitare inconsistenze nell'hash)
    if isinstance(content, dict) and "signature" in content:
        content = {k: v for k, v in content.items() if k != "signature"}

    # 3. Determina il tipo di contenuto e serializza in modo deterministico e calcola l'hash
    match content:
        case str():
            content_type = "text"
            content_bytes = content.encode("utf-8")

        case dict() | list() | int() | float() | bool() | type(None):
            content_type = "json"
            try:
                # Contenuto JSON serializzabile
                # Usa sort_keys=True per garantire ordine deterministico
                # Usa separators compatti per rimuovere spazi inutili
                json_str = json.dumps(content, sort_keys=True, separators=(",", ":"))
                content_bytes = json_str.encode("utf-8")

            except (TypeError, ValueError) as e:
                raise HTTPException(400, f"Content is not JSON serializable: {e}")

        case _:
            raise HTTPException(
                400,
                f"Unsupported content type: {type(content).__name__}. "
                "Only str, dict, list, int, float, bool, and None are supported.",
            )

    # 4. Calcola l'hash del contenuto
    content_hash = hashlib.sha256(content_bytes).hexdigest()

    # 5. Crea i metadata della firma
    metadata = SignatureMetadata(
        version="2.0",
        algorithm="RSA-PSS-SHA256",
        uid=user.uid,
        date=date,
        content_hash=content_hash,
        content_type=content_type,
    )

    # 6. Serializza i metadata in modo deterministico per la firma
    try:
        metadata_json = json.dumps(
            metadata.model_dump(), sort_keys=True, separators=(",", ":")
        )
        metadata_bytes = metadata_json.encode("utf-8")
    except Exception as e:
        raise HTTPException(500, f"Error serializing metadata: {e}")

    # 7. Firma i metadata (che includono l'hash del contenuto)
    # Nota: firmiamo solo i metadata, non il contenuto completo (più efficiente)
    try:
        signature_bytes = private_key.sign(
            metadata_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
    except Exception as e:
        raise HTTPException(500, f"Errore durante la firma: {e}")

    # 8. Converti la firma in base64 (standard per le API web)
    signature_b64 = base64.b64encode(signature_bytes).decode("ascii")

    # 9. Crea l'oggetto firma completo
    digital_signature = DigitalSignature(metadata=metadata, signature=signature_b64)

    # 10. Prepara il documento firmato
    # Se il contenuto è un dict, aggiungi la firma come proprietà
    if isinstance(content, dict):
        result = {**content, "signature": digital_signature.model_dump()}
    else:
        # Per contenuti non-dict (str, int, etc), crea un wrapper
        result = {"data": content, "signature": digital_signature.model_dump()}

    # 11. Restituisce il documento firmato
    return SignedDocument(**result)


##########################################################
# VERIFICA FIRMA
##########################################################


def verify_signed_document(
    document: SignedDocument,
    signer: AccountModel,
) -> SignatureVerificationResult:
    """
    Verifica la validità di un documento firmato digitalmente.

    Controlli eseguiti:
    1. Verifica che l'algoritmo sia supportato
    2. Ricalcola l'hash del contenuto
    3. Verifica che l'hash corrisponda (integrità)
    4. Verifica la firma digitale (autenticità)
    5. Controlla timestamp e altre anomalie

    Args:
        document: Documento firmato da verificare
        signer: AccountModel dell'utente firmatario

    Returns:
        SignatureVerificationResult: Risultato dettagliato della verifica

    Raises:
        HTTPException: Se ci sono errori critici
    """
    errors = []
    warnings = []
    content_integrity = False
    signature_authentic = False

    metadata = document.signature.metadata
    signature_b64 = document.signature.signature
    user = signer

    # 1. Verifica la versione e l'algoritmo
    if metadata.version != "2.0":
        warnings.append(f"Unsupported signature version: {metadata.version}")

    if metadata.algorithm != "RSA-PSS-SHA256":
        errors.append(f"Unsupported algorithm: {metadata.algorithm}")
        return SignatureVerificationResult(
            valid=False,
            signer_uid=metadata.uid,
            signer_email=user.email,
            signed_at=metadata.date,
            algorithm=metadata.algorithm,
            content_integrity=False,
            signature_authentic=False,
            errors=errors,
            warnings=warnings,
        )

    # 2. Estrae il contenuto originale (tutto tranne la signature)
    document_dict = document.model_dump()
    original_content = {k: v for k, v in document_dict.items() if k != "signature"}

    # Se il documento aveva solo 'data' e 'signature', estrai il valore di 'data'
    if len(original_content) == 1 and "data" in original_content:
        original_content = original_content["data"]

    # 3. Ricalcola l'hash del contenuto originale
    try:
        content_type, content_bytes = _serialize_and_hash_payload(original_content)
        calculated_hash = hashlib.sha256(content_bytes).hexdigest()
    except Exception as e:
        errors.append(f"Error serializing content: {e}")
        return SignatureVerificationResult(
            valid=False,
            signer_uid=metadata.uid,
            signer_email=user.email,
            signed_at=metadata.date,
            algorithm=metadata.algorithm,
            content_integrity=False,
            signature_authentic=False,
            errors=errors,
            warnings=warnings,
        )

    # 4. Verifica l'integrità del contenuto (confronto hash)
    if calculated_hash != metadata.content_hash:
        errors.append("Content has been modified (hash mismatch)")
    else:
        content_integrity = True

    # 5. Verifica che il tipo di contenuto corrisponda
    if content_type != metadata.content_type:
        warnings.append(
            f"Content type mismatch: expected {metadata.content_type}, got {content_type}"
        )

    # 6. Carica la chiave pubblica dell'utente
    try:
        public_key = serialization.load_pem_public_key(
            user.keychain.public_key.encode()
        )
    except Exception as e:
        errors.append(f"Error loading public key: {e}")
        return SignatureVerificationResult(
            valid=False,
            signer_uid=metadata.uid,
            signer_email=user.email,
            signed_at=metadata.date,
            algorithm=metadata.algorithm,
            content_integrity=content_integrity,
            signature_authentic=False,
            errors=errors,
            warnings=warnings,
        )

    # 7. Ricostruisce i metadata per la verifica
    metadata_json = json.dumps(
        metadata.model_dump(), sort_keys=True, separators=(",", ":")
    )
    metadata_bytes = metadata_json.encode("utf-8")

    # 8. Decodifica la firma da base64
    try:
        signature_bytes = base64.b64decode(signature_b64)
    except Exception as e:
        errors.append(f"Invalid signature encoding: {e}")
        return SignatureVerificationResult(
            valid=False,
            signer_uid=metadata.uid,
            signer_email=user.email,
            signed_at=metadata.date,
            algorithm=metadata.algorithm,
            content_integrity=content_integrity,
            signature_authentic=False,
            errors=errors,
            warnings=warnings,
        )

    # 9. Verifica la firma digitale
    try:
        public_key.verify(
            signature_bytes,
            metadata_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        signature_authentic = True
    except InvalidSignature:
        errors.append("Signature verification failed - signature is not authentic")
    except Exception as e:
        errors.append(f"Error during signature verification: {e}")

    # 10. Verifica della data
    try:
        signed_date = datetime.strptime(metadata.date, "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()

        # Se la firma è nel futuro, è sospetta
        if signed_date > today:
            warnings.append("Signature date is in the future")

        # Se la firma è molto vecchia (es: >5 anni), potrebbe essere da considerare scaduta
        age_days = (today - signed_date).days
        if age_days > 1825:  # ~5 anni
            warnings.append(f"Signature is very old ({age_days} days)")

    except Exception as e:
        warnings.append(f"Could not parse date: {e}")

    # 11. Determina validità complessiva
    valid = content_integrity and signature_authentic and len(errors) == 0

    return SignatureVerificationResult(
        valid=valid,
        signer_uid=metadata.uid,
        signer_email=user.email,
        signed_at=metadata.date,
        algorithm=metadata.algorithm,
        content_integrity=content_integrity,
        signature_authentic=signature_authentic,
        errors=errors,
        warnings=warnings,
    )


##########################################################
# FUNZIONI HELPER
##########################################################


def _serialize_and_hash_payload(content: Any) -> tuple[str, bytes, str]:
    """
    Serializza il contenuto in modo deterministico e crea l'hash.

    Args:
        content: Contenuto da serializzare (dict, str, int, float, etc.)

    Returns:
        tuple: (content_type, content_bytes, content_hash)
            - content_type: "json" o "text"
            - content_bytes: rappresentazione in bytes del contenuto
            - content_hash: hash SHA-256 del contenuto

    Raises:
        HTTPException: Se il contenuto non è serializzabile
    """
    if isinstance(content, str):
        # Contenuto testuale semplice
        t = "text"  # type
        b = content.encode("utf-8")  # bytes
        h = hashlib.sha256(b).hexdigest()  # hash
        return (t, b, h)

    elif isinstance(content, (dict, list, int, float, bool, type(None))):
        # Contenuto JSON serializzabile
        # Usa sort_keys=True per garantire ordine deterministico
        # Usa separators compatti per rimuovere spazi inutili
        try:
            json_str = json.dumps(content, sort_keys=True, separators=(",", ":"))
            t = "json"
            b = json_str.encode("utf-8")
            h = hashlib.sha256(b).hexdigest()
            return (t, b, h)

        except (TypeError, ValueError) as e:
            raise HTTPException(400, f"Content is not JSON serializable: {e}")
    else:
        raise HTTPException(
            400,
            f"Unsupported content type: {type(content).__name__}. "
            "Only str, dict, list, int, float, bool, and None are supported.",
        )
