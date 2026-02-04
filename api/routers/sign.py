from typing import Annotated
from fastapi import Body, Cookie, HTTPException, Header, Query, APIRouter
from controllers.auth import Auth, AuthenticatedUser, TokenClaims
from controllers.sign import generate_signature, verify_signature
from models import DataWithSignature, SignVerifyReport, SignModel
from datetime import datetime

router = APIRouter(tags=["signature"], prefix="/api/v1/sign")


@router.post("/object", response_model=DataWithSignature)
async def sign(
    user: AuthenticatedUser,
    data: Annotated[str | dict, Body(description="Dati da firmare")] = None,
    on: Annotated[
        str, Query(description="la data della firma, nel formato yyyy-mm-dd")
    ] = None,
):
    """
    Firma i dati forniti dall'utente autenticato.
    Restituisce un oggetto contenente la firma e le informazioni correlate.
    
    Args:
        user: L'utente autenticato che sta firmando i dati
        data: I dati da firmare (str o dict)
        on: La data della firma nel formato yyyy-mm-dd
        
    Returns:
        DataWithSignature: Un oggetto contenente i dati originali e la firma digitale
    """
    # Verifica che i dati siano forniti
    if data is None:
        raise HTTPException(400, "Dati da firmare non forniti")
    
    # Verifica che la data sia fornita
    if on is None:
        raise HTTPException(400, "Data della firma non fornita")
    
    try:
        # Verifica che la data sia formattata in modo corretto
        datetime.strptime(on, "%Y-%m-%d")
    except Exception:
        raise HTTPException(400, "Data non valida. Formato richiesto: yyyy-mm-dd")
    
    # Genera la firma digitale usando la chiave privata dell'utente
    signature = generate_signature(data=data, user=user, date=on)
    
    # Crea l'oggetto contenente i dati e la firma
    result = {
        "signature": signature.model_dump(),
    }
    
    # Aggiungi i dati originali all'oggetto
    if isinstance(data, dict):
        result.update(data)
    else:
        result["data"] = data
    
    return DataWithSignature(**result)


@router.post("/verify_signature", response_model=SignVerifyReport)
async def verify(
    data: Annotated[DataWithSignature, Body(description="I dati firmati")],
):
    """
    Verifica l'autenticità di un documento firmato digitalmente.
    
    Questo endpoint esegue le seguenti verifiche:
    - Valida che la firma sia autentica usando la chiave pubblica dell'utente
    - Verifica che il contenuto dei dati non sia stato modificato (confronto fingerprint)
    - Identifica l'utente che ha firmato il documento
    - Verifica la data della firma
    
    Args:
        data: Un oggetto DataWithSignature contenente i dati e la firma da verificare
        
    Returns:
        SignVerifyReport: Un report dettagliato della verifica con:
            - verified: True se tutte le verifiche hanno successo
            - uid: L'ID dell'utente che ha firmato
            - user: L'email dell'utente che ha firmato
            - date: La data della firma
            - fingerprint: L'hash SHA256 dei dati
            - errors: Lista di eventuali errori riscontrati
            - msg: Messaggio descrittivo del risultato
    """
    # Verifica che l'oggetto contenga la firma
    if not hasattr(data, 'signature') or data.signature is None:
        raise HTTPException(400, "L'oggetto non contiene una firma valida")
    
    # Verifica la firma digitale
    return await verify_signature(data)
