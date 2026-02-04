# 🚀 Quick Start: Sistema di Firma Digitale v2

## Installazione

Il sistema v2 è già pronto. Aggiungi il router alla tua applicazione FastAPI:

```python
# In main.py
from routers.sign_v2 import router as sign_router_v2

app.include_router(sign_router_v2)
```

---

## 📝 Esempio 1: Firma una Fattura

### Request
```http
POST /api/v2/sign/
Authorization: Bearer {your_token}
Content-Type: application/json

{
  "content": {
    "invoice_id": "INV-2026-001",
    "date": "2026-02-04",
    "amount": 1500.00,
    "currency": "EUR",
    "client": {
      "name": "Acme Corp",
      "vat": "IT12345678901"
    },
    "items": [
      {
        "description": "Consulenza IT",
        "quantity": 10,
        "price": 100.00
      },
      {
        "description": "Sviluppo Software",
        "quantity": 5,
        "price": 100.00
      }
    ]
  }
}
```

### Response
```json
{
  "content": {
    "invoice_id": "INV-2026-001",
    "date": "2026-02-04",
    "amount": 1500.00,
    "currency": "EUR",
    "client": {
      "name": "Acme Corp",
      "vat": "IT12345678901"
    },
    "items": [...]
  },
  "signature": {
    "metadata": {
      "version": "2.0",
      "algorithm": "RSA-PSS-SHA256",
      "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
      "timestamp": "2026-02-04T14:30:45.123456Z",
      "content_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
      "content_type": "json"
    },
    "signature": "MEUCIQDxG8vqz2dVBXm... (base64)"
  }
}
```

---

## ✅ Esempio 2: Verifica una Firma

### Request
```http
POST /api/v2/sign/verify
Content-Type: application/json

{
  "content": {
    "invoice_id": "INV-2026-001",
    "date": "2026-02-04",
    "amount": 1500.00,
    ...
  },
  "signature": {
    "metadata": {
      "version": "2.0",
      "algorithm": "RSA-PSS-SHA256",
      "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
      "timestamp": "2026-02-04T14:30:45.123456Z",
      "content_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
      "content_type": "json"
    },
    "signature": "MEUCIQDxG8vqz2dVBXm..."
  }
}
```

### Response (Verifica OK)
```json
{
  "valid": true,
  "signer_uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
  "signer_email": "mario.rossi@example.com",
  "signed_at": "2026-02-04T14:30:45.123456Z",
  "algorithm": "RSA-PSS-SHA256",
  "content_integrity": true,
  "signature_authentic": true,
  "errors": [],
  "warnings": []
}
```

### Response (Documento Modificato)
```json
{
  "valid": false,
  "signer_uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
  "signer_email": "mario.rossi@example.com",
  "signed_at": "2026-02-04T14:30:45.123456Z",
  "algorithm": "RSA-PSS-SHA256",
  "content_integrity": false,
  "signature_authentic": true,
  "errors": [
    "Content has been modified (hash mismatch)"
  ],
  "warnings": []
}
```

---

## 📝 Esempio 3: Firma un Messaggio di Testo

### Request
```http
POST /api/v2/sign/
Authorization: Bearer {your_token}
Content-Type: application/json

{
  "content": "Approvo il budget di 50.000 EUR per il progetto XYZ"
}
```

### Response
```json
{
  "content": "Approvo il budget di 50.000 EUR per il progetto XYZ",
  "signature": {
    "metadata": {
      "version": "2.0",
      "algorithm": "RSA-PSS-SHA256",
      "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
      "timestamp": "2026-02-04T15:22:10.987654Z",
      "content_hash": "b6a72e3f1d4c8a9b0e5f2d7c3a1b9e8f4d5c2a1b0e9f8d7c6a5b4e3d2c1a0b9",
      "content_type": "text"
    },
    "signature": "MFYwEAYHKoZIzj0CAQY... (base64)"
  }
}
```

---

## 🔍 Esempio 4: Ottenere Info sul Sistema

### Request
```http
GET /api/v2/sign/info
```

### Response
```json
{
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
    ...
  ],
  "best_practices": [
    "Always verify signatures before trusting content",
    "Store signed documents with their signatures",
    ...
  ]
}
```

---

## 💻 Esempio Python Client

```python
import requests
import json

# Configurazione
BASE_URL = "http://localhost:8000"
TOKEN = "your_access_token"

def sign_document(content):
    """Firma un documento"""
    response = requests.post(
        f"{BASE_URL}/api/v2/sign/",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={"content": content}
    )
    return response.json()

def verify_document(signed_document):
    """Verifica un documento firmato"""
    response = requests.post(
        f"{BASE_URL}/api/v2/sign/verify",
        headers={"Content-Type": "application/json"},
        json=signed_document
    )
    return response.json()

# Esempio di utilizzo
if __name__ == "__main__":
    # 1. Crea una fattura
    invoice = {
        "invoice_id": "INV-2026-001",
        "amount": 1500.00,
        "currency": "EUR"
    }
    
    # 2. Firma la fattura
    signed = sign_document(invoice)
    print("✅ Fattura firmata")
    print(json.dumps(signed, indent=2))
    
    # 3. Verifica la firma
    result = verify_document(signed)
    print(f"\n{'✅' if result['valid'] else '❌'} Verifica: {result['valid']}")
    print(f"Firmato da: {result['signer_email']}")
    print(f"Data: {result['signed_at']}")
    
    # 4. Modifica i dati (simula attacco)
    signed['content']['amount'] = 999999.99
    
    # 5. Ri-verifica (dovrebbe fallire)
    result = verify_document(signed)
    print(f"\n{'✅' if result['valid'] else '❌'} Verifica dopo modifica: {result['valid']}")
    print(f"Errori: {result['errors']}")
```

---

## 🔐 Esempio JavaScript/TypeScript

```typescript
// types.ts
interface SignRequest {
  content: any;
}

interface SignedDocument {
  content: any;
  signature: {
    metadata: {
      version: string;
      algorithm: string;
      uid: string;
      timestamp: string;
      content_hash: string;
      content_type: "json" | "text";
    };
    signature: string;
  };
}

interface VerificationResult {
  valid: boolean;
  signer_uid: string;
  signer_email: string;
  signed_at: string;
  algorithm: string;
  content_integrity: boolean;
  signature_authentic: boolean;
  errors: string[];
  warnings: string[];
}

// client.ts
class SignatureClient {
  constructor(
    private baseUrl: string,
    private token: string
  ) {}

  async signDocument(content: any): Promise<SignedDocument> {
    const response = await fetch(`${this.baseUrl}/api/v2/sign/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    });
    
    if (!response.ok) {
      throw new Error(`Signature failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  async verifyDocument(document: SignedDocument): Promise<VerificationResult> {
    const response = await fetch(`${this.baseUrl}/api/v2/sign/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(document)
    });
    
    if (!response.ok) {
      throw new Error(`Verification failed: ${response.statusText}`);
    }
    
    return response.json();
  }
}

// Esempio di utilizzo
const client = new SignatureClient('http://localhost:8000', 'your_token');

const invoice = {
  invoice_id: 'INV-2026-001',
  amount: 1500.00,
  currency: 'EUR'
};

// Firma
const signed = await client.signDocument(invoice);
console.log('✅ Document signed:', signed);

// Verifica
const result = await client.verifyDocument(signed);
console.log(`${result.valid ? '✅' : '❌'} Valid:`, result.valid);
console.log(`Signed by:`, result.signer_email);
```

---

## 📚 Best Practices

### ✅ DO
- **Sempre verifica** le firme prima di fidarti del contenuto
- **Salva** i documenti firmati completi (content + signature)
- **Logga** tutte le operazioni di firma/verifica per audit
- **Usa HTTPS** in produzione
- **Implementa rate limiting** sugli endpoint di firma
- **Backup** periodici delle chiavi (in modo sicuro)

### ❌ DON'T
- **NON** modificare il contenuto dopo la firma
- **NON** separare content e signature (salva insieme)
- **NON** riutilizzare firme per contenuti diversi
- **NON** fidarti di firme senza verificarle
- **NON** esporre chiavi private

---

## 🔧 Troubleshooting

### Errore: "Content has been modified"
**Causa**: Il contenuto è stato modificato dopo la firma  
**Soluzione**: Il documento non è più valido, richiedi una nuova firma

### Errore: "Signature verification failed"
**Causa**: La firma non è autentica o la chiave è errata  
**Soluzione**: Verifica che l'utente esista e che la chiave sia corretta

### Errore: "Signer user not found"
**Causa**: L'utente che ha firmato non esiste più  
**Soluzione**: L'utente è stato eliminato, il documento non è verificabile

### Warning: "Signature is very old"
**Causa**: La firma ha più di 5 anni  
**Soluzione**: Considera di richiedere una nuova firma (policy aziendale)

---

## 📞 Supporto

- 📖 Documentazione completa: `SIGNATURE_REVIEW.md`
- 🧪 Test comparativi: `python test_signature_comparison.py`
- 🔄 Script migrazione: `python migrate_signatures.py`
- 📧 Contatta l'amministratore per problemi con le chiavi

---

**Ultima revisione**: 4 Febbraio 2026  
**Versione**: 2.0  
**Status**: ✅ Production Ready
