"""
Router per il sistema di firma digitale v2.0

Endpoints migliorati con maggiore sicurezza ed efficienza.
"""

from typing import Annotated
from fastapi import Body, APIRouter, HTTPException
from controllers.auth import AuthenticatedUser
from controllers.sign.sign import sign_content, verify_signed_document
from models.sign import SignedDocument, SignatureVerificationResult, SignRequest

router = APIRouter(tags=["signature"], prefix="/api/v2/sign")


@router.post("/", response_model=SignedDocument, summary="Firma un documento")
async def sign_document(
    user: AuthenticatedUser,
    request: Annotated[SignRequest, Body(description="Contenuto da firmare")],
):
    """
    Firma digitalmente un documento usando il sistema v2.0.

    ## Miglioramenti rispetto a v1:
    - ✅ Usa JSON invece di pickle (sicuro, portabile)
    - ✅ Serializzazione deterministica (risultati consistenti)
    - ✅ Firma solo l'hash (efficiente per file grandi)
    - ✅ Timestamp preciso con timezone UTC
    - ✅ Versioning del protocollo
    - ✅ Firma in base64 (standard web)
    - ✅ Struttura più pulita e standard-compliant

    ## Utilizzo:

    ```json
    {
      "content": {
        "invoice_id": "INV-2026-001",
        "amount": 1500.00,
        "currency": "EUR"
      }
    }
    ```

    ## Risposta:

    ```json
    {
      "content": {...},
      "signature": {
        "metadata": {
          "version": "2.0",
          "algorithm": "RSA-PSS-SHA256",
          "uid": "user-uuid",
          "timestamp": "2026-02-04T14:30:00Z",
          "content_hash": "abc123...",
          "content_type": "json"
        },
        "signature": "MEUCIQDxG..."
      }
    }
    ```

    Args:
        user: Utente autenticato (automatico tramite token)
        request: Oggetto contenente il contenuto da firmare

    Returns:
        SignedDocument: Documento firmato con metadata completi

    Raises:
        400: Se il contenuto non è serializzabile
        500: Se la firma fallisce
    """
    if request.content is None:
        raise HTTPException(400, "Content to sign cannot be None")

    return sign_content(content=request.content, user=user)


@router.post(
    "/verify",
    response_model=SignatureVerificationResult,
    summary="Verifica una firma digitale",
)
async def verify_document(
    document: Annotated[
        SignedDocument, Body(description="Documento firmato da verificare")
    ],
):
    """
    Verifica l'autenticità e l'integrità di un documento firmato.

    ## Verifiche eseguite:
    1. ✅ Recupera l'utente firmatario dal database
    2. ✅ Verifica supporto versione e algoritmo
    3. ✅ Ricalcola l'hash del contenuto
    4. ✅ Verifica integrità (hash match)
    5. ✅ Verifica autenticità della firma (chiave pubblica)
    6. ✅ Controlla timestamp per anomalie
    7. ✅ Fornisce report dettagliato con errori e warning

    ## Utilizzo:

    ```json
    {
      "content": {...},
      "signature": {
        "metadata": {...},
        "signature": "..."
      }
    }
    ```

    ## Risposta (successo):

    ```json
    {
      "valid": true,
      "signer_uid": "user-uuid",
      "signer_email": "user@example.com",
      "signed_at": "2026-02-04T14:30:00Z",
      "algorithm": "RSA-PSS-SHA256",
      "content_integrity": true,
      "signature_authentic": true,
      "errors": [],
      "warnings": []
    }
    ```

    ## Risposta (fallimento):

    ```json
    {
      "valid": false,
      "signer_uid": "user-uuid",
      "signer_email": "user@example.com",
      "signed_at": "2026-02-04T14:30:00Z",
      "algorithm": "RSA-PSS-SHA256",
      "content_integrity": false,
      "signature_authentic": false,
      "errors": [
        "Content has been modified (hash mismatch)",
        "Signature verification failed"
      ],
      "warnings": []
    }
    ```

    Args:
        document: Documento firmato da verificare

    Returns:
        SignatureVerificationResult: Report dettagliato della verifica

    Raises:
        500: Se ci sono errori critici nel processo di verifica
    """
    return await verify_signed_document(document)


@router.get(
    "/info",
    summary="Informazioni sul sistema di firma v2.0",
    response_model=dict,
)
async def signature_system_info():
    """
    Restituisce informazioni sul sistema di firma digitale v2.0.

    Include:
    - Versione del protocollo
    - Algoritmi supportati
    - Miglioramenti rispetto a v1
    - Best practices

    Returns:
        dict: Informazioni sul sistema
    """
    return {
        "version": "2.0",
        "protocol": "Custom Digital Signature (JWS-inspired)",
        "supported_algorithms": ["RSA-PSS-SHA256"],
        "key_size": "2048 bits",
        "hash_algorithm": "SHA-256",
        "encoding": "base64",
        "timestamp_format": "ISO8601 with UTC timezone",
        "improvements_over_v1": [
            "Uses JSON instead of pickle (security)",
            "Signs only hash + metadata (efficiency)",
            "Precise timestamps with timezone",
            "Protocol versioning",
            "Deterministic serialization",
            "Base64 signature (web standard)",
            "Separate content_integrity and signature_authentic checks",
            "Warnings for suspicious signatures",
        ],
        "best_practices": [
            "Always verify signatures before trusting content",
            "Store signed documents with their signatures",
            "Consider signature age in your security policy",
            "Implement key rotation policies",
            "Log all signature operations for audit trail",
        ],
    }
