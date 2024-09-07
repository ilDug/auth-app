from os import environ as env

AUTH_SERVER_URL = "http://localhost:8000" if not env["AUTH_HOST"] else env["AUTH_HOST"]
AUTHENTICATION_URL = f"{AUTH_SERVER_URL}/auth/authenticate"
AUTHORIZATION_URL = f"{AUTH_SERVER_URL}/auth/authorize"
