"""
Modelli per il sistema di firma digitale v2.0

Questo sistema implementa un approccio più sicuro e standard-compliant
per la firma digitale di documenti.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal, Any
from datetime import datetime


class SignatureMetadata(BaseModel):
    """Metadati della firma digitale"""

    version: Literal["2.0"] = "2.0"  # versione del protocollo di firma
    algorithm: Literal["RSA-PSS-SHA256"] = "RSA-PSS-SHA256"  # algoritmo utilizzato
    uid: str = Field(description="User ID del firmatario")
    date: str = Field(
        description="Data della firma nel formato yyyy-mm-dd"
    )  # es: 2026-02-04
    content_hash: str = Field(description="SHA-256 hash del contenuto")
    content_type: Literal["text", "json"] = Field(
        description="Tipo di contenuto firmato"
    )


class DigitalSignature(BaseModel):
    """Firma digitale completa"""

    metadata: SignatureMetadata
    signature: str = Field(description="Firma digitale in formato base64")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "version": "2.0",
                    "algorithm": "RSA-PSS-SHA256",
                    "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
                    "date": "2026-02-04",
                    "content_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
                    "content_type": "json",
                },
                "signature": "MEUCIQDxG...",
            }
        }
    )


class SignedDocument(BaseModel):
    """Documento firmato digitalmente

    La firma viene aggiunta come proprietà dell'oggetto originale.
    Tutti gli altri campi dell'oggetto originale vengono preservati.
    """

    signature: DigitalSignature = Field(description="Firma digitale del documento")

    model_config = ConfigDict(
        extra="allow",  # Permette campi extra per includere il contenuto originale
        json_schema_extra={
            "example": {
                "invoice_id": "INV-2026-001",
                "amount": 1500.00,
                "currency": "EUR",
                "signature": {
                    "metadata": {
                        "version": "2.0",
                        "algorithm": "RSA-PSS-SHA256",
                        "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
                        "date": "2026-02-04",
                        "content_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
                        "content_type": "json",
                    },
                    "signature": "MEUCIQDxG...",
                },
            }
        },
    )


class SignatureVerificationResult(BaseModel):
    """Risultato della verifica della firma"""

    valid: bool = Field(description="True se la firma è valida")
    signer_uid: str = Field(description="UID del firmatario")
    signer_email: EmailStr = Field(description="Email del firmatario")
    signed_at: str = Field(description="Data della firma (yyyy-mm-dd)")
    algorithm: str = Field(description="Algoritmo utilizzato")
    content_integrity: bool = Field(
        description="True se il contenuto non è stato modificato"
    )
    signature_authentic: bool = Field(
        description="True se la firma è autentica"
    )
    errors: list[str] = Field(default_factory=list, description="Lista di errori")
    warnings: list[str] = Field(
        default_factory=list, description="Lista di avvisi"
    )

    @property
    def message(self) -> str:
        """Genera un messaggio descrittivo del risultato"""
        if self.valid:
            return f"Document validly signed by {self.signer_email} at {self.signed_at}"
        else:
            return f"Invalid signature: {'; '.join(self.errors)}"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valid": True,
                "signer_uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
                "signer_email": "mario.rossi@example.com",
                "signed_at": "2026-02-04",
                "algorithm": "RSA-PSS-SHA256",
                "content_integrity": True,
                "signature_authentic": True,
                "errors": [],
                "warnings": [],
            }
        }
    )


class SignRequest(BaseModel):
    """Richiesta di firma"""

    content: Any = Field(description="Contenuto da firmare (dict o str)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": {
                    "invoice_id": "INV-2026-001",
                    "amount": 1500.00,
                    "currency": "EUR"
                }
            }
        }
    )
