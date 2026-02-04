# Sistema di Firma Digitale - Guida all'uso

## Panoramica

Il sistema di firma digitale implementato utilizza la crittografia asimmetrica (RSA) per garantire:
- **Autenticità**: Verifica che il documento sia stato firmato dall'utente dichiarato
- **Integrità**: Garantisce che i dati non siano stati modificati dopo la firma
- **Non ripudio**: L'utente non può negare di aver firmato il documento

## Flusso di Lavoro

### 1. Firma dei Dati (`POST /api/v1/sign/object`)

L'endpoint permette di firmare dati di tipo `str` o `dict` utilizzando la chiave privata dell'utente autenticato.

#### Richiesta

```bash
POST /api/v1/sign/object?on=2026-02-04
Authorization: Bearer {token}
Content-Type: application/json

{
  "data": {
    "invoice_id": "INV-2026-001",
    "amount": 1500.00,
    "currency": "EUR",
    "client": "Acme Corp"
  }
}
```

oppure per dati semplici:

```bash
POST /api/v1/sign/object?on=2026-02-04
Authorization: Bearer {token}
Content-Type: application/json

{
  "data": "Questo è un messaggio importante"
}
```

#### Risposta

```json
{
  "invoice_id": "INV-2026-001",
  "amount": 1500.00,
  "currency": "EUR",
  "client": "Acme Corp",
  "signature": {
    "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
    "date": "2026-02-04",
    "fingerprint": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    "signature": "3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b..."
  }
}
```

#### Campi della Firma

- **uid**: Identificatore univoco dell'utente che ha firmato
- **date**: Data della firma nel formato yyyy-mm-dd
- **fingerprint**: Hash SHA-256 dei dati (per verificare l'integrità)
- **signature**: Firma digitale generata con la chiave privata dell'utente

### 2. Verifica della Firma (`POST /api/v1/sign/verify_signature`)

L'endpoint verifica l'autenticità di un documento firmato.

#### Richiesta

```bash
POST /api/v1/sign/verify_signature
Content-Type: application/json

{
  "invoice_id": "INV-2026-001",
  "amount": 1500.00,
  "currency": "EUR",
  "client": "Acme Corp",
  "signature": {
    "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
    "date": "2026-02-04",
    "fingerprint": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    "signature": "3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b..."
  }
}
```

#### Risposta (Verifica Riuscita)

```json
{
  "verified": true,
  "date": "2026-02-04",
  "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
  "user": "mario.rossi@example.com",
  "fingerprint": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
  "errors": [],
  "msg": "Document correctly signed by mario.rossi@example.com on 04/02/2026"
}
```

#### Risposta (Verifica Fallita)

```json
{
  "verified": false,
  "date": "2026-02-04",
  "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
  "user": "mario.rossi@example.com",
  "fingerprint": "b692b7e41cg531515b122844dgc8c201e73d76cg0cdeb43c68c388e0be0g257f",
  "errors": [
    "fingerprint non corrispondente",
    "data or signature not authentic"
  ],
  "msg": "Errors in signature verification: fingerprint non corrispondente; data or signature not authentic"
}
```

## Sicurezza

### Processo di Firma

1. I dati vengono serializzati (pickle per dict, encoding per str)
2. Viene calcolato un hash SHA-256 dei dati (fingerprint)
3. Viene creato un payload contenente: uid, date, e dati in formato esadecimale
4. Il payload viene firmato usando la chiave privata dell'utente con algoritmo RSA-PSS

### Processo di Verifica

1. Estrae la firma e i dati dall'oggetto ricevuto
2. Recupera la chiave pubblica dell'utente dal database
3. Ricalcola il fingerprint dei dati ricevuti
4. Verifica che il fingerprint corrisponda a quello nella firma
5. Verifica la firma digitale usando la chiave pubblica
6. Restituisce un report dettagliato della verifica

### Algoritmi Utilizzati

- **Firma**: RSA con PSS padding (Probabilistic Signature Scheme)
- **Hash**: SHA-256
- **Gestione Chiavi**: Crittografia asimmetrica RSA
- **Serializzazione**: Pickle per oggetti complessi, UTF-8 per stringhe

## Casi d'Uso

### 1. Fatture Elettroniche
Firma digitale di fatture per garantire autenticità e non ripudio.

### 2. Contratti Digitali
Firma di accordi e contratti tra parti.

### 3. Documenti Aziendali
Approvazione e firma di documenti interni con tracciabilità.

### 4. Messaggi Importanti
Firma di comunicazioni critiche per garantire provenienza.

### 5. Log di Audit
Firma di log per garantire che non siano stati manomessi.

## Errori Comuni

### 400 - Data non valida
La data deve essere nel formato `yyyy-mm-dd` (es: 2026-02-04)

### 400 - Dati da firmare non forniti
Il campo `data` è obbligatorio nella richiesta di firma

### 400 - L'oggetto non contiene una firma valida
Durante la verifica, l'oggetto deve contenere il campo `signature`

### 404 - Utente non trovato
L'utente che ha firmato il documento non esiste più nel database

### Verifica fallita - fingerprint non corrispondente
I dati sono stati modificati dopo la firma

### Verifica fallita - data or signature not authentic
La firma non è valida o è stata generata con una chiave diversa

## Note Tecniche

- Le chiavi RSA di ogni utente sono memorizzate nel campo `keychain` dell'`AccountModel`
- La data della firma è inclusa nel payload firmato per evitare replay attacks
- Il fingerprint SHA-256 garantisce l'integrità dei dati
- La firma RSA-PSS offre maggiore sicurezza rispetto al padding standard
- I dati dict vengono serializzati con pickle, quindi mantengono la struttura completa
