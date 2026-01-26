from os import environ as env
from pathlib import Path
import json

ROOT = Path("/app")
MODE = env["MODE"] if "MODE" in env else "DEVELOPMENT"
FRONTEND_HOST = (
    env["FRONTEND_HOST"] if "FRONTEND_HOST" in env else "http://localhost:4200"
)
# HOST = "https://auth.dag.lan" if MODE == "PRODUCTION" else "http://localhost:8000"


REGISTRATION_BEHAVIOUR = (
    env["REGISTRATION_BEHAVIOUR"]
    if "REGISTRATION_BEHAVIOUR" in env
    else "ALLOW_ANYBODY"
)
"""
definisce il comportamento del sistema di registrazione

se impostato su ALLOW_ANYBODY, chiunque può registrarsi direttamente dall'API

se impostato su ONLY_ADMIN, solo gli admin possono creare nuovi utenti
"""

# JWT
###############################
KEY_PATH = Path("/run/secrets/JWT_KEY")
JWT_KEY = KEY_PATH.read_text() if KEY_PATH.exists() else "fake_key_for_dev_only"
CERT_PATH = Path("/run/secrets/JWT_CERT")
JWT_CERT = CERT_PATH.read_text() if CERT_PATH.exists() else "fake_cert_for_dev_only"

ACTIVATION_KEY_LENGTH = 64
AUTH_TOKEN_LIFE = 24 * 30  # trenta giorni
REFRESH_TOKEN_LIFE = 24 * 30  # trenta giorni
FINGERPRINT_COOKIE_LIFE = 3600 * 24 * 30  # trenta giorni


# STATIC FILES
###############################
ASSETS_PATH = ROOT / "assets"


COOKIES_SETTINGS = {
    "secure": True,
    "httponly": True,
    "samesite": "lax",
    "expires": FINGERPRINT_COOKIE_LIFE,
}


# CORS
###############################
CORS = {
    "allow_credentials": True,
    "allow_origins": [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        FRONTEND_HOST,
    ],
    "allow_methods": ["OPTIONS", "POST", "PUT", "GET", "DELETE"],
    "expose_headers": [
        "Origin",
        "Content-Type",
        "Set-Cookie",
        "X-Error",
        "X-Auth-Token",
        "Authorization",
        "X-Dag-Head",
        # "Access-Control-Expose-Headers"
    ],
    "allow_headers": [
        "Origin",
        "Content-Type",
        "Set-Cookie",
        "X-Error",
        "Accept",
        "Authorization",
        # "Access-Control-Expose-Headers"
    ],
}


# MONGO
###############################################
MONGO_HOST = env["MONGO_HOST"] if "MONGO_HOST" in env else "mongo.fake.lan:27017"
MONGO_USER = env["MONGO_USER"] if "MONGO_USER" in env else "fake_user"
DB = env["MONGO_DB"] if "MONGO_DB" in env else "fake_db"
MONGO_PW_PATH = Path("/run/secrets/MONGO_USER_PW")
MONGO_PW = MONGO_PW_PATH.read_text() if MONGO_PW_PATH.exists() else "fake_mongo_pw"
MONGO_CS = f"mongodb://{MONGO_USER}:{MONGO_PW}@{MONGO_HOST}/{DB}?authSource=admin"

# MAIL
###############################
MAIL_CONFIG_PATH = Path("/run/secrets/MAIL_CONFIG")
MAIL_CONFIG = (
    json.loads(MAIL_CONFIG_PATH.read_text())
    if MAIL_CONFIG_PATH.exists()
    else {
        "host": "mail.xxx.com",
        "port": 465,
        "user": "user@xxx.com",
        "password": "xxxxxxxxxxxxx",
    }
)

# email template PATH
ET_PATH = ROOT / "lib/templates"

# EMAIL TEMPLATES
ET_USER_ACTIVATION = ET_PATH / "user-activation.html"
ET_PASSWORD_RECOVER = ET_PATH / "recover-password.html"
