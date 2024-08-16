from core.auth import JWT
from core.config import AUTH_TOKEN_LIFE, REFRESH_TOKEN_LIFE
from ..models import AccountAccessModel, AccountModel, JWTAuth


class Tokens:
    @classmethod
    def generate_bundle(cls, user: AccountModel) -> tuple[str, str, AccountAccessModel]:
        """genera il token, il fingerprint e il modello di accesso"""

        jwt = JWT()
        fingerprint, fingerprint_hash = jwt.fingerprint()

        payload = {
            **user.model_dump(exclude={"id", "hashed_password", "registration_date"}),
            "fingerprint_hash": fingerprint_hash,
        }

        token: str = jwt.create(payload, duration=AUTH_TOKEN_LIFE)
        jti: JWTAuth = jwt.verify(token).jti
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
