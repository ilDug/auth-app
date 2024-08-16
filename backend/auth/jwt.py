from uuid import uuid4
import hashlib
import jwt
from datetime import datetime, timedelta
from cryptography.x509 import load_pem_x509_certificate
from fastapi import HTTPException
from core.config import JWT_CERT, JWT_KEY, AUTH_TOKEN_LIFE
from models import JWTModel, AccountModel, AccountAccessModel


class JWT:
    """Classe Controller per la creazione e la verifica dey JWT"""

    CERT: str = JWT_CERT
    KEY: str = JWT_KEY

    def __base_payload(self, duration: int) -> dict:
        """genera il payload monimi per la creazione del token"""
        now = datetime.now()
        delta = timedelta(hours=3)
        before = now - delta

        nbf = {"nbf": before}
        iat = {"iat": before}
        exp = {"exp": now + timedelta(hours=duration)}
        jti = {"jti": str(uuid4())}
        payload = {**nbf, **iat, **exp, **jti}

        return payload

    def create(self, claims: dict, duration=AUTH_TOKEN_LIFE) -> str:
        """genera il token in base al payload/claims passati come argomento. Duration [ore] (24*30 = 720)"""
        try:
            payload = self.__base_payload(duration)
            payload = {**payload, **claims}

            # crea il token (stringa)
            token = jwt.encode(payload, self.KEY, algorithm="RS256")
            return token

        except Exception as e:
            raise HTTPException(500, "ERRORE di crezione del token jwt: " + str(e))

    def verify(self, token: str) -> JWTModel:
        try:
            cert_obj = load_pem_x509_certificate(self.CERT.encode())
            public_key = cert_obj.public_key()
            # private_key = cert_obj.private_key()
            decoded = jwt.decode(token, public_key, algorithms=["RS256"])
            return JWTModel(**decoded)

        except Exception as e:
            raise HTTPException(500, "ERRORE di verifica del token jwt: " + str(e))

    def fingerprint(self) -> tuple[str, str]:
        """genera un fingerprint casuale e il suo hash"""

        fingerprint = str(uuid4())
        fingerprint_hash = hashlib.sha256(fingerprint.encode()).hexdigest()

        return fingerprint, fingerprint_hash

    def generate_tokens_bundle(
        self, user: AccountModel
    ) -> tuple[str, str, AccountAccessModel]:
        """genera il token, il fingerprint e il modello di accesso"""

        fingerprint, fingerprint_hash = self.fingerprint()

        payload = {
            **user.model_dump(exclude={"id", "hashed_password", "registration_date"}),
            "fingerprint_hash": fingerprint_hash,
        }

        token: str = self.create(payload)
        jti: str = self.verify(token).jti
        access = AccountAccessModel(uid=user.uid, jti=jti)

        return token, fingerprint, access

        # refresh_token: str = JWT.create(
        #     {
        #         "fingerprint_hash": fingerprint_hash,
        #         "passcode": str(uuid.uuid4()),
        #     },
        #     duration=REFRESH_TOKEN_LIFE,
        # )

        # refresh_jwt: JWTRefresh = JWT.verify(refresh_token)
