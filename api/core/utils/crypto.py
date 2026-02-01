from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class UserKeyChain(BaseModel):
    """coppia di chiavi"""

    public_key: str  # public key
    private_key: str  # private key

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_name=True,
        validate_by_alias=True,
    )


def generate_crypto_keys() -> UserKeyChain:
    """genera la coppia di chiavi crittografiche"""

    # generate the private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # generate the public key
    public_key = private_key.public_key()

    # serialize the private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # serialize the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # return the keys as strings
    return UserKeyChain(
        private_key=private_pem.decode(),
        public_key=public_pem.decode(),
    )
