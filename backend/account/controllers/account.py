import uuid
import hashlib
import bcrypt
from string import Template
from datetime import datetime
from fastapi import HTTPException
from pymongo import MongoClient
from models import AccountModel, LoginResponse, AccountActionKeyModel
from auth import JWT
from .security import generate_crypto_keys

# from core import DagMail, DagMailConfig
from core.utils import random_string
from core.config import (
    ACTIVATION_KEY_LENGTH,
    MONGO_CS,
    DB,
    MAIL_CONFIG,
    ET_USER_ACTIVATION,
    FRONTEND_HOST,
)
from core.email import DagMail, DagMailConfig


class Account:
    ACTIVATION_SCOPE = "account_activation"
    USER_NAMESPACE = uuid.UUID("24198490-e89c-4771-a941-ec2137d55905")
    ACTIVATION_LINK = f"{FRONTEND_HOST}/account/activate"

    @classmethod
    def verify_credential_arguments(cls, email: str, password: str) -> tuple[str, str]:
        """verifica che i parametri di login siano corretti"""

        if not email:
            raise HTTPException(400, "il campo email non è specificato")

        if not password:
            raise HTTPException(400, "la richiesta non contiene la password")

        email = email.lower().strip()

        return email, password

    @classmethod
    def login(cls, email: str, password: str) -> tuple[LoginResponse, str]:
        """si connette al server e restituisce il la LoginResponse e il fingerprint per i cookies"""

        email, password = cls.verify_credential_arguments(email, password)

        with MongoClient(MONGO_CS) as c:
            # controlla che l'utente sia presente nel database
            user = c[DB].accounts.find_one({"email": email})

            if user is None:
                raise HTTPException(
                    404,
                    "Utente non registrato. Procedi prima con la registrazione del tuo account.",
                )
            user = AccountModel(**user)

            # verifica la password
            if not bcrypt.checkpw(
                password.encode(), user.hashed_password.get_secret_value().encode()
            ):
                raise HTTPException(500, "password non corretta per questo account.")

            # crea i tokens e gli oggetti JWT
            jwt = JWT()
            (token, fingerprint) = jwt.generate_tokens_bundle(user)

            return LoginResponse(dat=token), fingerprint

    @classmethod
    def register(
        cls, email: str, password: str, notify: bool = True
    ) -> tuple[LoginResponse, str]:
        """registra l'utente e  ritorna i dati di accesso"""

        email, password = cls.verify_credential_arguments(email, password)

        # controlla che l'utente esista
        email_hash = hashlib.md5(email.encode()).hexdigest()
        if cls.exists(email_hash):
            raise HTTPException(
                400, "un utente con questa nome esiste gia' nel database"
            )
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode(), salt).decode()
        uid = uuid.uuid5(cls.USER_NAMESPACE, email)

        # default username is the email without the domain part
        username = email.split("@")[0]

        with MongoClient(MONGO_CS) as c:
            with c.start_session() as s:
                with s.start_transaction() as t:
                    # cerca se la chiave di attivazione esiste
                    while True:
                        activation_key = random_string(ACTIVATION_KEY_LENGTH)
                        if (
                            cursor := c[DB].account_actions_keys.find_one(
                                {"key": activation_key}
                            )
                            is None
                        ):
                            break

                    # inserisce il nuovo utente
                    account = {
                        "uid": str(uid),
                        "username": username,
                        "email": email,
                        "active": False,
                        "authorizations": ["basic"],
                        "hashed_password": hashed_pw,
                        "registration_date": datetime.now(),
                        "keychain": generate_crypto_keys().model_dump(),
                    }
                    id = c[DB].accounts.insert_one(account).inserted_id

                    if id is None:
                        raise HTTPException(500, str("errore inserimento nuovo utente"))

                    # genera una chiave di attivazione e la inserisce
                    account_action_key = AccountActionKeyModel(
                        uid=str(uid),
                        key=activation_key,
                        created_at=datetime.now(),
                        used_at=None,
                        scope=cls.ACTIVATION_SCOPE,
                    )
                    id = (
                        c[DB]
                        .account_actions_keys.insert_one(
                            account_action_key.model_dump()
                        )
                        .inserted_id
                    )

                    if id is None:
                        raise HTTPException(
                            500, "errore generazione chiave di attivazione"
                        )

                    # manda la mail di attivazione
                    if notify:
                        if not cls.send_activation_email(email, activation_key):
                            print(f"errore invio mail di attivazione {datetime.now()}")
                            raise HTTPException(
                                500,
                                "registrazione effettuata correttamente, ma con errore invio mail di attivazione. Prova a richiedere di nuovo l'email di attivazione.",
                            )

                return cls.login(email, password)

    @classmethod
    def exists(cls, email_hash: str) -> bool:
        """verifica se l'utente esiste nel database"""
        with MongoClient(MONGO_CS) as c:
            emails = [
                hashlib.md5(e["email"].encode()).hexdigest()
                for e in c[DB].accounts.find({}, {"email": 1, "_id": 0})
            ]

        return email_hash in emails

    @classmethod
    def send_activation_email(cls, email: str, activation_key: str) -> bool:
        """manda la email con il codice di attivazione dell'account,
        @return boolean se la mail è stata invata"""

        link = f"{cls.ACTIVATION_LINK}/{activation_key}"
        template = ET_USER_ACTIVATION.read_text()
        body = Template(template).substitute(ACTIVATION_LINK=link)

        try:
            config = DagMailConfig(**MAIL_CONFIG)
            with DagMail(config) as ms:
                ms.add_receiver(email)
                ms.messageHTML(body, "Attivazione Account")
                ms.send()
                return True
        except Exception as e:
            print(str(e))
            return False
