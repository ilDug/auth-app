"""
Router per il sistema di firma digitale v2.0

Endpoints migliorati con maggiore sicurezza ed efficienza.
"""

from typing import Annotated, Any
from fastapi import Body, APIRouter, HTTPException, Query
from controllers.auth import AuthenticatedUser
from controllers.sign import sign_content, verify_signed_document
from controllers.account import Account
from models.sign import SignatureVerificationResult, SignatureMetadata
from datetime import datetime

router = APIRouter(tags=["signature"], prefix="/api/auth/v2/sign")


@router.post("/", summary="Firma un documento")
async def sign_document(
    user: AuthenticatedUser,
    document: Annotated[Any, Body(description="Contenuto da firmare")],
    on: Annotated[str, Query(description="Data della firma nel formato yyyy-mm-dd")],
):
    """
    Firma digitalmente un documento usando il sistema v2.0.

    Args:
        user: Utente autenticato (automatico tramite token)
        document: Contenuto da firmare (qualsiasi tipo JSON-serializzabile)
        on: Data della firma nel formato yyyy-mm-dd

    Returns:
        Documento firmato con metadata completi

    Raises:
        400: Se il contenuto non è serializzabile o la data non è valida
        500: Se la firma fallisce
    """
    if document is None:
        raise HTTPException(400, "Content to sign cannot be None")

    # Valida il formato della data
    try:
        datetime.strptime(on, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use yyyy-mm-dd")

    return sign_content(content=document, user=user, date=on)


@router.post(
    "/verify",
    response_model=SignatureVerificationResult,
    summary="Verifica una firma digitale",
)
async def verify_document(
    document: Annotated[dict, Body(description="Documento firmato da verificare")],
):
    """
    Verifica l'autenticità e l'integrità di un documento firmato.

    Args:
        document: Documento firmato da verificare

    Returns:
        SignatureVerificationResult: Report dettagliato della verifica

    Raises:
        404: Se l'utente firmatario non esiste
        500: Se ci sono errori critici nel processo di verifica
    """

    # Recupera l'utente firmatario dal database
    metadata = SignatureMetadata(**document["signature"]["metadata"])
    try:
        signer = await Account.get_user(uid=metadata.uid)
    except HTTPException as e:
        if e.status_code == 404:
            # Utente non trovato - restituisco un risultato di verifica fallita
            return SignatureVerificationResult(
                valid=False,
                signer_uid=metadata.uid,
                signer_email="unknown@unknown.com",
                signed_at=metadata.date,
                algorithm=metadata.algorithm,
                content_integrity=False,
                signature_authentic=False,
                errors=[f"Signer user not found: {metadata.uid}"],
                warnings=[],
            )
        # Altri errori vengono rilanciati
        raise

    # Verifica il documento passando l'utente recuperato
    return verify_signed_document(document, signer)
