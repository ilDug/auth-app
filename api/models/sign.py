from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel
from typing import Annotated, Literal


class SignatureMetadata(BaseModel):
    """Metadati della firma digitale"""

    version: Literal["2.0"] = "2.0"  # versione del protocollo di firma
    algorithm: Literal["RSA-PSS-SHA256"] = "RSA-PSS-SHA256"  # algoritmo utilizzato
    uid: Annotated[str, Field(description="User ID del firmatario")]
    date: Annotated[str, Field(description="Data della firma nel formato yyyy-mm-dd")]
    content_hash: Annotated[str, Field(description="SHA-256 hash del contenuto")]
    content_type: Annotated[
        Literal["text", "json"],
        Field(description="Tipo di contenuto firmato"),
    ]

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_name=True,
    )


class DigitalSignature(BaseModel):
    """Firma digitale completa"""

    metadata: SignatureMetadata
    signature: Annotated[str, Field(description="Firma digitale in formato base64")]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "version": "2.0",
                    "algorithm": "RSA-PSS-SHA256",
                    "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
                    "date": "2026-02-04",
                    "contentHash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
                    "contentType": "json",
                },
                "signature": "MEUCIQDxG...",
            }
        }
    )


class SignatureVerificationResult(BaseModel):
    """Risultato della verifica della firma"""

    valid: Annotated[bool, Field(description="True se la firma è valida")]
    signer_uid: Annotated[str, Field(description="UID del firmatario")]
    signer_email: Annotated[EmailStr, Field(description="Email del firmatario")]
    signed_at: Annotated[str, Field(description="Data della firma (yyyy-mm-dd)")]
    algorithm: Annotated[str, Field(description="Algoritmo utilizzato")]
    content_integrity: Annotated[
        bool, Field(description="True se il contenuto non è stato modificato")
    ]
    signature_authentic: Annotated[
        bool, Field(description="True se la firma è autentica")
    ]
    errors: Annotated[
        list[str], Field(default_factory=list, description="Lista di errori")
    ]
    warnings: Annotated[
        list[str], Field(default_factory=list, description="Lista di avvisi")
    ]

    @property
    def message(self) -> str:
        """Genera un messaggio descrittivo del risultato"""
        if self.valid:
            return f"Document validly signed by {self.signer_email} at {self.signed_at}"
        else:
            return f"Invalid signature: {'; '.join(self.errors)}"

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        json_schema_extra={
            "example": {
                "valid": True,
                "signerUid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
                "signerEmail": "mario.rossi@example.com",
                "signedAt": "2026-02-04",
                "algorithm": "RSA-PSS-SHA256",
                "contentIntegrity": True,
                "signatureAuthentic": True,
                "errors": [],
                "warnings": [],
            }
        },
    )
