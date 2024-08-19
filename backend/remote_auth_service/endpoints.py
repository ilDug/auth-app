# from os import environ as env

AUTH_HOST = "localhost:8000"  # env["AUTH_HOST"]
AUTH_SERVER_URL = f"http://{AUTH_HOST}/auth"

AUTHENTICATION_URL = f"{AUTH_SERVER_URL}/auth/authenticate?claims=True"
AUTHORIZATION_URL = f"{AUTH_SERVER_URL}/auth/authorize"
