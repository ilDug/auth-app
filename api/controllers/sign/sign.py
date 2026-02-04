"""
Sistema di Firma Digitale v2.0

Implementazione migliorata con:
- JSON invece di pickle (sicurezza)
- Firma solo dell'hash (efficienza)
- Timestamp precisi (audit trail)
- Versioning del protocollo (manutenibilità)
- Serializzazione deterministica (affidabilità)
- Base64 per firma (standard web)
"""

from datetime import datetime, timezone
import hashlib
import json
import base64
from typing import Any
from fastapi import HTTPException
from models import AccountModel
from models.sign import (
    SignatureMetadata,
    DigitalSignature,
    SignedDocument,
    SignatureVerificationResult,
)
from controllers.account import Account
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


##########################################################
# FIRMA DIGITALE
##########################################################


def sign_content(content: Any, user: AccountModel, date: str) -> SignedDocument:
    """
    Firma digitalmente un contenuto usando la chiave privata dell'utente.

    Vantaggi rispetto alla versione precedente:
    - Usa JSON invece di pickle (sicuro e portabile)
    - Serializzazione deterministica (risultati consistenti)
    - Firma solo l'hash + metadata (efficiente)
    - Data della firma esplicita (tracciabilità)
    - Versioning del protocollo
    - Firma in base64 (standard web)

    Args:
        content: Contenuto da firmare (dict o str)
        user: Utente autenticato che firma
        date: Data della firma nel formato yyyy-mm-dd

    Returns:
        SignedDocument: Documento firmato con metadata

    Raises:
        HTTPException: Se il contenuto non è serializzabile o la firma fallisce
    """
    # 1. Determina il tipo di contenuto e serializza in modo deterministico
    content_type, content_bytes = _serialize_content(content)

    # 2. Calcola l'hash SHA-256 del contenuto
    content_hash = hashlib.sha256(content_bytes).hexdigest()

    # 3. Crea i metadata della firma
    metadata = SignatureMetadata(
        version="2.0",
        algorithm="RSA-PSS-SHA256",
        uid=user.uid,
        date=date,
        content_hash=content_hash,
        content_type=content_type,
    )

    # 4. Serializza i metadata in modo deterministico per la firma
    metadata_json = json.dumps(
        metadata.model_dump(), sort_keys=True, separators=(",", ":")
    )
    metadata_bytes = metadata_json.encode("utf-8")

    # 5. Carica la chiave privata dell'utente
    try:
        private_key = serialization.load_pem_private_key(
            user.keychain.private_key.encode(), password=None
        )
    except Exception as e:
        raise HTTPException(500, f"Errore nel caricamento della chiave privata: {e}")

    # 6. Firma i metadata (che includono l'hash del contenuto)
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

    # 7. Converti la firma in base64 (standard per le API web)
    signature_b64 = base64.b64encode(signature_bytes).decode("ascii")

    # 8. Crea l'oggetto firma completo
    digital_signature = DigitalSignature(metadata=metadata, signature=signature_b64)

    # 9. Prepara il documento firmato
    # Se il contenuto è un dict, aggiungi la firma come proprietà
    if isinstance(content, dict):
        # Rimuove signature se già presente (per evitare duplicati)
        content_copy = {k: v for k, v in content.items() if k != "signature"}
        result = {**content_copy, "signature": digital_signature.model_dump()}
    else:
        # Per contenuti non-dict (str, int, etc), crea un wrapper
        result = {"data": content, "signature": digital_signature.model_dump()}

    # 10. Restituisce il documento firmato
    return SignedDocument(**result)


##########################################################
# VERIFICA FIRMA
##########################################################


async def verify_signed_document(
    document: SignedDocument,
) -> SignatureVerificationResult:
    """
    Verifica la validità di un documento firmato digitalmente.

    Controlli eseguiti:
    1. Recupera l'utente dal database
    2. Verifica che l'algoritmo sia supportato
    3. Ricalcola l'hash del contenuto
    4. Verifica che l'hash corrisponda (integrità)
    5. Verifica la firma digitale (autenticità)
    6. Controlla timestamp e altre anomalie

    Args:
        document: Documento firmato da verificare

    Returns:
        SignatureVerificationResult: Risultato dettagliato della verifica

    Raises:
        HTTPException: Se l'utente non esiste o ci sono errori critici
    """
    errors = []
    warnings = []
    content_integrity = False
    signature_authentic = False

    metadata = document.signature.metadata
    signature_b64 = document.signature.signature

    # 1. Recupera l'utente dal database
    try:
        user = await Account.get_user(uid=metadata.uid)
    except HTTPException as e:
        if e.status_code == 404:
            errors.append(f"Signer user not found: {metadata.uid}")
            return SignatureVerificationResult(
                valid=False,
                signer_uid=metadata.uid,
                signer_email="unknown@unknown.com",
                signed_at=metadata.date,
                algorithm=metadata.algorithm,
                content_integrity=False,
                signature_authentic=False,
                errors=errors,
            )
        raise

    # 2. Verifica la versione e l'algoritmo
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

    # 3. Estrae il contenuto originale (tutto tranne la signature)
    document_dict = document.model_dump()
    original_content = {k: v for k, v in document_dict.items() if k != "signature"}

    # Se il documento aveva solo 'data' e 'signature', estrai il valore di 'data'
    if len(original_content) == 1 and "data" in original_content:
        original_content = original_content["data"]

    # 4. Ricalcola l'hash del contenuto originale
    try:
        content_type, content_bytes = _serialize_content(original_content)
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

    # 5. Verifica l'integrità del contenuto (confronto hash)
    if calculated_hash != metadata.content_hash:
        errors.append("Content has been modified (hash mismatch)")
    else:
        content_integrity = True

    # 6. Verifica che il tipo di contenuto corrisponda
    if content_type != metadata.content_type:
        warnings.append(
            f"Content type mismatch: expected {metadata.content_type}, got {content_type}"
        )

    # 7. Carica la chiave pubblica dell'utente
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

    # 8. Ricostruisce i metadata per la verifica
    metadata_json = json.dumps(
        metadata.model_dump(), sort_keys=True, separators=(",", ":")
    )
    metadata_bytes = metadata_json.encode("utf-8")

    # 9. Decodifica la firma da base64
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

    # 10. Verifica la firma digitale
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

    # 11. Verifica della data
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

    # 12. Determina validità complessiva
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


def _serialize_content(content: Any) -> tuple[str, bytes]:
    """
    Serializza il contenuto in modo deterministico.

    Args:
        content: Contenuto da serializzare (dict, str, int, float, etc.)

    Returns:
        tuple: (content_type, content_bytes)
            - content_type: "json" o "text"
            - content_bytes: rappresentazione in bytes del contenuto

    Raises:
        HTTPException: Se il contenuto non è serializzabile
    """
    if isinstance(content, str):
        # Contenuto testuale semplice
        return ("text", content.encode("utf-8"))

    elif isinstance(content, (dict, list, int, float, bool, type(None))):
        # Contenuto JSON serializzabile
        # Usa sort_keys=True per garantire ordine deterministico
        # Usa separators compatti per rimuovere spazi inutili
        try:
            json_str = json.dumps(content, sort_keys=True, separators=(",", ":"))
            return ("json", json_str.encode("utf-8"))
        except (TypeError, ValueError) as e:
            raise HTTPException(
                400, f"Content is not JSON serializable: {e}"
            )

    else:
        raise HTTPException(
            400,
            f"Unsupported content type: {type(content).__name__}. "
            "Only str, dict, list, int, float, bool, and None are supported.",
        )


def get_content_hash(content: Any) -> str:
    """
    Calcola l'hash SHA-256 di un contenuto senza firmarlo.
    Utile per verifiche preliminari o confronti.

    Args:
        content: Contenuto di cui calcolare l'hash

    Returns:
        str: Hash SHA-256 in formato esadecimale
    """
    _, content_bytes = _serialize_content(content)
    return hashlib.sha256(content_bytes).hexdigest()
