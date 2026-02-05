# 🔐 Client di Autenticazione/Autorizzazione Remota

Questo modulo fornisce un client pronto all'uso per integrare l'autenticazione e l'autorizzazione remota in qualsiasi progetto FastAPI.

## 📋 Indice

- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Utilizzo Base](#utilizzo-base)
- [Dependencies Disponibili](#dependencies-disponibili)
- [Router per Proxy Endpoints](#router-per-proxy-endpoints)
- [Esempi Pratici](#esempi-pratici)
- [Struttura File](#struttura-file)

---

## 📦 Installazione

### 1. Copia la cartella `client` nel tuo progetto

```bash
cp -r path/to/auth-app/api/client path/to/your-project/
```

### 2. Installa le dipendenze necessarie

```bash
pip install fastapi httpx certifi
```

---

## ⚙️ Configurazione

### File: `endpoints.py`

Configura le variabili d'ambiente per puntare al tuo server di autenticazione:

```python
# endpoints.py
AUTH_SERVER_URL = "http://localhost:8000"  # URL del server di autenticazione
AUTHENTICATION_URL = f"{AUTH_SERVER_URL}/auth/authenticate"
AUTHORIZATION_URL = f"{AUTH_SERVER_URL}/auth/authorize"

# Certificato CA per connessioni HTTPS sicure
CA_CERT_PATH = Path("/run/secrets/CA_CERT") if Path("/run/secrets/CA_CERT").exists() else certifi.where()
```

#### Configurazione tramite variabile d'ambiente:

```bash
export AUTH_HOST="https://auth.example.com"
```

Se `AUTH_HOST` è impostata, sovrascriverà il valore di default.

---

## 🚀 Utilizzo Base

### 1. Importa il router e le dependencies nel tuo `main.py`

```python
from fastapi import FastAPI
from client import auth_router
from client.middlewares import AuthenticationGuard, UserId, AuthPermissions

app = FastAPI()

# Registra il router per proxy degli endpoint di autenticazione
app.include_router(auth_router)
```

### 2. Usa le dependencies negli endpoint

```python
from fastapi import APIRouter
from client.middlewares import AuthenticationGuard, UserId, UserEmail

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(
    authenticated: AuthenticationGuard,  # Verifica che l'utente sia autenticato
    user_id: UserId,                      # Ottiene l'ID dell'utente
    email: UserEmail,                     # Ottiene l'email dell'utente
):
    return {
        "message": "Accesso autorizzato",
        "user_id": user_id,
        "email": email
    }
```

---

## 🔑 Dependencies Disponibili

Tutte le dependencies sono definite in `middlewares.py` e possono essere iniettate negli endpoint FastAPI.

### `AuthenticationGuard`
**Tipo**: `bool`  
**Scopo**: Verifica che l'utente sia autenticato  
**Solleva**: `HTTPException 401` se non autenticato

```python
@router.get("/dashboard")
async def dashboard(authenticated: AuthenticationGuard):
    # Se arrivi qui, l'utente è autenticato
    return {"message": "Benvenuto nella dashboard"}
```

---

### `AuthClaims`
**Tipo**: `dict`  
**Scopo**: Restituisce tutti i claims dell'utente (UID, email, autorizzazioni, ecc.)

```python
@router.get("/profile")
async def profile(claims: AuthClaims):
    return {
        "uid": claims.get("uid"),
        "email": claims.get("email"),
        "authorizations": claims.get("authorizations", [])
    }
```

---

### `UserId`
**Tipo**: `str`  
**Scopo**: Restituisce l'ID univoco dell'utente autenticato

```python
@router.get("/my-data")
async def my_data(user_id: UserId):
    # user_id contiene l'UID dell'utente
    data = get_user_data_from_db(user_id)
    return data
```

---

### `UserEmail`
**Tipo**: `str`  
**Scopo**: Restituisce l'email dell'utente autenticato

```python
@router.get("/send-notification")
async def send_notification(email: UserEmail):
    send_email(email, "Notifica importante")
    return {"sent_to": email}
```

---

### `AuthPermissions`
**Tipo**: `list`  
**Scopo**: Restituisce la lista dei permessi dell'utente

```python
@router.get("/admin/users")
async def list_users(permissions: AuthPermissions):
    if "admin" not in permissions:
        raise HTTPException(403, "Permesso negato")
    
    return {"users": get_all_users()}
```

---

### `IsAdmin`
**Tipo**: `bool`  
**Scopo**: Verifica che l'utente abbia il permesso di `admin`  
**Solleva**: `HTTPException` se non è admin

```python
@router.delete("/users/{user_id}")
async def delete_user(user_id: str, is_admin: IsAdmin):
    # Se arrivi qui, l'utente è admin
    delete_user_from_db(user_id)
    return {"deleted": user_id}
```

---

## 🔄 Router per Proxy Endpoints

Il file `auth_router.py` fornisce un router che fa da **proxy** verso il server di autenticazione remoto.

### Endpoints disponibili (automaticamente inoltrati):

#### Account Management
- `POST /api/v2/account/login` - Login utente
- `POST /api/v2/account/register` - Registrazione nuovo utente
- `GET /api/v2/account/exists/{email_md5_hash}` - Verifica esistenza account
- `GET /api/v2/account/activate/{key}` - Attivazione account
- `GET /api/v2/account/resend-activation/{email_md5_hash}` - Rinvia email attivazione
- `POST /api/v2/account/password/recover` - Recupero password
- `GET /api/v2/account/password/restore/init/{key}` - Inizia ripristino password
- `POST /api/v2/account/password/restore/set` - Imposta nuova password

#### Authentication & Authorization
- `GET /api/v2/auth/authenticate` - Verifica autenticazione
- `GET /api/v2/auth/authorize` - Verifica autorizzazione
- `POST /api/v2/auth/sign` - Firma digitale documento
- `POST /api/v2/auth/verify_signature` - Verifica firma digitale

#### User Management
- `GET /api/v2/users` - Lista utenti (richiede autenticazione)
- `GET /api/v2/users/{user_id}` - Dettagli utente
- `PUT /api/v2/users` - Aggiorna utente
- `DELETE /api/v2/users/{user_id}` - Elimina utente

### Come funziona il proxy

Tutti gli endpoint sopra elencati vengono automaticamente inoltrati al server di autenticazione configurato in `endpoints.py`. Il client:

1. ✅ Inoltra headers (incluso `Authorization`)
2. ✅ Inoltra cookies (incluso `fingerprint`)
3. ✅ Inoltra query parameters
4. ✅ Gestisce errori di rete e timeout
5. ✅ Propaga gli errori dal server remoto

---

## 💡 Esempi Pratici

### Esempio 1: Endpoint protetto base

```python
from fastapi import APIRouter
from client.middlewares import AuthenticationGuard, UserId

router = APIRouter()

@router.get("/my-profile")
async def my_profile(
    authenticated: AuthenticationGuard,
    user_id: UserId
):
    """
    Endpoint accessibile solo da utenti autenticati.
    Restituisce i dati del profilo dell'utente.
    """
    profile = fetch_profile_from_db(user_id)
    return profile
```

---

### Esempio 2: Endpoint con controllo permessi custom

```python
from fastapi import APIRouter, HTTPException
from client.middlewares import AuthClaims

router = APIRouter()

@router.post("/documents/{doc_id}/publish")
async def publish_document(
    doc_id: str,
    claims: AuthClaims
):
    """
    Pubblica un documento.
    Richiede il permesso 'publisher' o 'admin'.
    """
    permissions = claims.get("authorizations", [])
    
    if "publisher" not in permissions and "admin" not in permissions:
        raise HTTPException(403, "Permesso negato: richiesto ruolo publisher o admin")
    
    publish_doc(doc_id)
    return {"status": "published", "doc_id": doc_id}
```

---

### Esempio 3: Endpoint solo per admin

```python
from fastapi import APIRouter
from client.middlewares import IsAdmin, UserId

router = APIRouter()

@router.get("/admin/audit-log")
async def audit_log(
    is_admin: IsAdmin,
    admin_id: UserId
):
    """
    Visualizza i log di audit del sistema.
    Accessibile solo agli amministratori.
    """
    logs = fetch_audit_logs()
    
    # Log dell'accesso da parte dell'admin
    log_admin_action(admin_id, "viewed_audit_logs")
    
    return {"logs": logs}
```

---

### Esempio 4: Combinazione di dependencies

```python
from fastapi import APIRouter
from client.middlewares import UserId, UserEmail, AuthPermissions

router = APIRouter()

@router.get("/dashboard/stats")
async def dashboard_stats(
    user_id: UserId,
    email: UserEmail,
    permissions: AuthPermissions
):
    """
    Dashboard personalizzata in base ai permessi dell'utente.
    """
    stats = {
        "user_id": user_id,
        "email": email,
        "access_level": "admin" if "admin" in permissions else "user",
        "available_features": get_features_for_permissions(permissions)
    }
    
    return stats
```

---

## 📁 Struttura File

```
client/
├── __init__.py                 # Esporta middlewares e router
├── README.md                   # Questa documentazione
├── endpoints.py                # Configurazione URL e certificati
├── middlewares.py              # Dependencies per FastAPI
├── auth_fn.py                  # Funzioni di autenticazione/autorizzazione
└── auth_router.py              # Router proxy per endpoints remoti
```

### Descrizione dettagliata dei file:

#### `endpoints.py`
Contiene la configurazione degli endpoint del server remoto e il path al certificato CA per connessioni HTTPS.

#### `middlewares.py`
Definisce tutte le dependencies di FastAPI che possono essere iniettate negli endpoint:
- `AuthenticationGuard`: Guard per verificare autenticazione
- `AuthClaims`: Ottiene tutti i claims
- `UserId`: Ottiene l'UID
- `UserEmail`: Ottiene l'email
- `AuthPermissions`: Ottiene lista permessi
- `IsAdmin`: Verifica permesso admin

#### `auth_fn.py`
Implementa le funzioni che:
- Eseguono chiamate HTTP al server remoto
- Gestiscono errori di rete e timeout
- Estraggono informazioni specifiche dai claims
- Forniscono le funzioni base usate dalle dependencies

#### `auth_router.py`
Router FastAPI che fa da proxy trasparente verso il server di autenticazione, inoltrando tutti gli endpoint di account, auth e user management.

#### `__init__.py`
Esporta le dependencies e il router per un import semplificato.

---

## 🔒 Sicurezza

### Headers richiesti

Gli endpoint protetti richiedono:
- **`Authorization`** header con il Bearer token
- **`fingerprint`** cookie per validazione sessione

### Esempio di chiamata client:

```bash
curl -X GET "https://your-api.com/protected" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -b "fingerprint=YOUR_FINGERPRINT_VALUE"
```

### Gestione errori

Il client gestisce automaticamente:
- ✅ Errori di connessione (503)
- ✅ Timeout (504)
- ✅ Errori HTTP dal server remoto (propagati)
- ✅ Errori di autenticazione/autorizzazione (401/403)

---

## 🐛 Troubleshooting

### Errore: "Missing Authorization Header or Fingerprint"
**Soluzione**: Assicurati che il client invii l'header `Authorization` e il cookie `fingerprint`.

### Errore: "Errore di connessione con Auth Server"
**Soluzione**: Verifica che `AUTH_HOST` sia configurato correttamente e che il server sia raggiungibile.

### Errore: Certificate verification failed
**Soluzione**: 
- Verifica che `CA_CERT_PATH` punti al certificato CA corretto
- In sviluppo, puoi usare `verify=False` (NON in produzione!)

---

## 📝 Note

- Il client usa **httpx** per chiamate HTTP asincrone
- Tutti i log sono strutturati tramite il modulo `logging` di Python
- Le dependencies sono type-hinted per migliore supporto IDE
- Il codice è compatibile con FastAPI 0.100+

---

## 🤝 Supporto

Per problemi o domande, contatta il team di sviluppo del server di autenticazione.
