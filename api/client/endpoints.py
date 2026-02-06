from os import environ as env
from pathlib import Path
import certifi

AUTH_SERVER_URL = env.get("AUTH_HOST", "http://localhost:8000")
AUTHENTICATION_URL = f"{AUTH_SERVER_URL}/auth/authenticate"
AUTHORIZATION_URL = f"{AUTH_SERVER_URL}/auth/authorize"

# Path to your custom CA certificate bundle
CA_CERT_PATH = (
    Path("/run/secrets/CA_CERT")
    if Path("/run/secrets/CA_CERT").exists()
    else certifi.where()
)
