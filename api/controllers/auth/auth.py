import hashlib
from . import JWT
from fastapi import HTTPException
from models import JWTModel


class Auth(JWT):
    def authenticate(
        self, auth_header: str, fingerprint: str, claims: bool = False
    ) -> bool | dict:
        ##### HEADER
        if not auth_header:
            raise HTTPException(
                401, "Unauthorized - l'header non contiene il valore Authorization"
            )

        if not auth_header.startswith("Bearer "):
            raise HTTPException(401, "Unauthorized - l'header non è valido")

        ##### JWT
        token = auth_header.replace("Bearer ", "")

        try:
            jwt: JWTModel = self.verify(token)
        except Exception as e:
            raise HTTPException(
                401, "Unauthorized - il token non è valido (VERIFY ERROR)"
            )

        if True:
            if fingerprint is None:
                raise HTTPException(401, "Unauthorized - fingerprint assente")

            if jwt.fingerprint_hash != hashlib.sha256(fingerprint.encode()).hexdigest():
                raise HTTPException(
                    401, "Unauthorized - il fingerprint non corrisponde"
                )

        ##### RETURN
        return jwt.model_dump() if claims else True

    def authorize(self, auth_header: str, fingerprint: str, permission: str):
        claims = self.authenticate(auth_header, fingerprint, claims=True)
        if permission in claims["authorizations"]:
            return True
        else:
            raise HTTPException(
                403, "Forbidden - Unauthorized for permission: " + permission
            )
