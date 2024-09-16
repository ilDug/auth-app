from os import environ as env
from pathlib import Path
import json

ROOT = Path("/app")
MODE = env["MODE"]
FRONTEND_HOST = env["FRONTEND_HOST"]
# HOST = "https://auth.dag.lan" if MODE == "PRODUCTION" else "http://localhost:8000"


# JWT
###############################
JWT_KEY = Path("/run/secrets/JWT_KEY").read_text()
JWT_CERT = Path("/run/secrets/JWT_CERT").read_text()
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
MONGO_HOST = env["MONGO_HOST"]  # host:password
MONGO_USER = env["MONGO_USER"]
DB = env["MONGO_DB"]
MONGO_PW = Path("/run/secrets/MONGO_USER_PW").read_text()
MONGO_CS = f"mongodb://{MONGO_USER}:{MONGO_PW}@{MONGO_HOST}/{DB}?authSource=admin"

# MAIL
###############################
MAIL_CONFIG_PATH = Path("/run/secrets/MAIL_CONFIG")
MAIL_CONFIG = json.loads(MAIL_CONFIG_PATH.read_text())

# email template PATH
ET_PATH = ROOT / "lib/templates"

# EMAIL TEMPLATES
ET_USER_ACTIVATION = ET_PATH / "user-activation.html"
ET_PASSWORD_RECOVER = ET_PATH / "recover-password.html"
