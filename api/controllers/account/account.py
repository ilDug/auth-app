import hashlib
import bcrypt
import asyncio
from string import Template
from fastapi import HTTPException
from pymongo import MongoClient, AsyncMongoClient
from pydantic import SecretStr
from models import (
    AccountModel,
    LoginResponse,
    AccountActionKeyModel,
    AccountRegistrationModel,
)
from datetime import datetime
from ..auth import JWT

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
    ACTIVATION_LINK = f"{FRONTEND_HOST}/account/activate"

    @classmethod
    async def login(cls, email: str, password: SecretStr) -> tuple[LoginResponse, str]:
        """si connette al server e restituisce il la LoginResponse e il fingerprint per i cookies"""

        async with AsyncMongoClient(MONGO_CS) as c:
            # controlla che l'utente sia presente nel database
            user = await c[DB].accounts.find_one({"email": email})

            if user is None:
                raise HTTPException(
                    404,
                    "Utente non registrato. Procedi prima con la registrazione del tuo account.",
                )
            user = AccountModel(**user)

            # verifica la password in modo async (bcrypt è CPU-intensive)
            is_valid_password: bool = await asyncio.to_thread(
                bcrypt.checkpw,
                password.get_secret_value().encode(),
                user.password_hash.encode(),
            )

            if not is_valid_password:
                raise HTTPException(500, "password non corretta per questo account.")

            # crea i tokens e gli oggetti JWT
            jwt = JWT()
            token, fingerprint = jwt.bundle(user)

            return LoginResponse(dat=token), fingerprint

    @classmethod
    async def register(
        cls,
        user: AccountRegistrationModel,
        notify: bool = True,
    ) -> tuple[LoginResponse, str]:
        """registra l'utente e  ritorna i dati di accesso"""

        # controlla che l'utente esista
        if await cls.exists(user.email_hash):
            raise HTTPException(
                400,
                "un utente con questa nome esiste gia' nel database",
            )

        with MongoClient(MONGO_CS) as c:
            with c.start_session() as s:
                with s.start_transaction():
                    # cerca se la chiave di attivazione esiste
                    while True:
                        activation_key = random_string(ACTIVATION_KEY_LENGTH)
                        if (
                            c[DB].account_actions_keys.count_documents(
                                {"key": activation_key}, session=s
                            )
                            == 0
                        ):
                            break

                    # inserisce il nuovo utente
                    if (
                        c[DB]
                        .accounts.insert_one(user.model_dump(), session=s)
                        .inserted_id
                        is None
                    ):
                        s.abort_transaction()
                        raise HTTPException(500, str("errore inserimento nuovo utente"))

                    try:
                        # genera una chiave di attivazione e la inserisce
                        account_action_key = AccountActionKeyModel(
                            uid=str(user.uid),
                            key=activation_key,
                            scope=cls.ACTIVATION_SCOPE,
                        )
                    except Exception as e:
                        s.abort_transaction()
                        raise HTTPException(500, f"errore generazione chiave: {str(e)}")

                    if (
                        c[DB]
                        .account_actions_keys.insert_one(
                            account_action_key.model_dump(), session=s
                        )
                        .inserted_id
                        is None
                    ):
                        s.abort_transaction()
                        raise HTTPException(
                            500, "errore generazione chiave di attivazione"
                        )

                # transazione completata con successo
                # ora manda la mail FUORI dalla transazione (non è un'operazione DB)
                if notify:
                    if not await cls.send_activation_email(user.email, activation_key):
                        print(f"errore invio mail di attivazione {datetime.now()}")
                        raise HTTPException(
                            500,
                            "registrazione effettuata correttamente, ma con errore invio mail di attivazione. Prova a richiedere di nuovo l'email di attivazione.",
                        )

        return await cls.login(user.email, user.password)

    @classmethod
    async def exists(cls, email_hash: str) -> bool:
        """verifica se l'utente esiste nel database"""
        async with AsyncMongoClient(MONGO_CS) as c:
            accounts = (
                await c[DB].accounts.find({}, {"email": 1, "_id": 0}).to_list(None)
            )

            # esegui l'hashing MD5 in thread pool per evitare blocchi su grandi dataset
            emails = await asyncio.to_thread(
                lambda: [hashlib.md5(e["email"].encode()).hexdigest() for e in accounts]
            )

        return email_hash in emails

    @classmethod
    async def send_activation_email(cls, email: str, activation_key: str) -> bool:
        """manda la email con il codice di attivazione dell'account,
        @return boolean se la mail è stata invata"""

        link = f"{cls.ACTIVATION_LINK}/{activation_key}"

        # leggi il template in modo asincrono
        template = await asyncio.to_thread(ET_USER_ACTIVATION.read_text)
        body = Template(template).substitute(ACTIVATION_LINK=link)

        # esegui l'invio email in thread pool (operazione I/O bloccante)
        def _send_email():
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

        return await asyncio.to_thread(_send_email)
