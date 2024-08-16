from os import environ as env
from pathlib import Path

ROOT = Path("/app")
MODE = env["MODE"]

# JWT
###############################
JWT_KEY = (ROOT / "lib/keys/auth.key").read_text()
JWT_CERT = (ROOT / "lib/certs/auth.crt").read_text()
ACTIVATION_KEY_LENGTH = 64
AUTH_TOKEN_LIFE = 24 * 30  # trenta giorni
REFRESH_TOKEN_LIFE = 24 * 30  # trenta giorni
FINGERPRINT_COOKIE_LIFE = 3600 * 24 * 30  # trenta giorni

# DB
###############################
USERS_PATH = ROOT / "lib/db/users.yaml"
AUTHORIZATIONS_PATH = ROOT / "lib/db/authorizations.yaml"
ACCESSES_PATH = ROOT / "lib/db/accesses"

# STATIC FILES
###############################
ASSETS_PATH = ROOT / "assets"


# CORS
###############################
CORS = {
    "allow_credentials": True,
    "allow_origins": [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
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
