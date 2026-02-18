from argon2 import PasswordHasher
import asyncio
from string import Template
from email_validator import validate_email
from datetime import datetime, timedelta
from fastapi import HTTPException
from icecream import ic
from pydantic import SecretStr
from pymongo import AsyncMongoClient, MongoClient
from core.email import DagMail, DagMailConfig
from core.utils.string import random_string
from models import AccountModel, AccountActionKeyModel
from .account import Account

from core.config import (
    ET_PASSWORD_RECOVER,
    MAIL_CONFIG,
    MONGO_CS,
    ACTIVATION_KEY_LENGTH,
    DB,
    FRONTEND_HOST,
)

# #############################################################################################
# #################  PASSWORD #################################################################
# #############################################################################################


class Password(Account):

    RECOVER_SCOPE = "recover_password"
    RECOVER_LINK = f"{FRONTEND_HOST}/account/password/restore"

    @classmethod
    async def recover(cls, email: str) -> bool:
        """genera una chiave di attivazione che permette di ripristinare la password. Restituisce la key via email"""

        # controlla se l'email è presente e se è di un formato valido
        if not email:
            raise HTTPException(400, "il campo email non è specificato")

        email = email.lower().strip()

        try:
            validate_email(email)
        except Exception:
            raise HTTPException(400, "indirizzo email non valido")

        async with AsyncMongoClient(MONGO_CS) as c:

            # cerca l'utente nel database
            user = await c[DB].accounts.find_one({"email": email})
            if user is None:
                raise HTTPException(400, "indirizzo email non presente nel database")
            user = AccountModel(**user)

            # crea  la chiave di attivazione esiste e controlla che non esista già nel database
            while True:
                recover_key = random_string(ACTIVATION_KEY_LENGTH)
                count = await c[DB].account_actions_keys.count_documents(
                    {"key": recover_key}
                )
                if count == 0:
                    break

            # inserisce la chiave nel database
            key = AccountActionKeyModel(
                uid=str(user.uid),
                key=recover_key,
                scope=cls.RECOVER_SCOPE,
            )
            id = (
                await c[DB].account_actions_keys.insert_one(key.db_dump())
            ).inserted_id

            if id is None:
                raise HTTPException(500, "Errore creazione chiave di recupero")

            # manda l'email di recover password
            if not await cls.send_recover_email(email, recover_key):
                raise HTTPException(
                    500, "Errore nell recupero della password,  prova più tardi"
                )
            else:
                return True

    @classmethod
    async def restore_init(cls, key: str) -> dict:
        """esegui i controlli della chiave e restituisce l'AccountModel dell'utente per procedere con il set della password"""

        async with AsyncMongoClient(MONGO_CS) as c:
            r = await c[DB].account_actions_keys.find_one({"key": key})
            if r is None:
                raise HTTPException(500, "chiave di recupero inesistente")
            operation = AccountActionKeyModel(**r)

            if operation.scope != cls.RECOVER_SCOPE:
                raise HTTPException(
                    400,
                    "la chiave fornita non e' adatta per il recupero della password",
                )

            if operation.used_at is not None:
                raise HTTPException(400, "la chiave fornita e' gia' stata utilizzata")

            limit_date = operation.created_at + timedelta(hours=1)
            if datetime.now() > limit_date:
                raise HTTPException(400, "la chiave fornita e' scaduta")

            user = await c[DB].accounts.find_one({"uid": operation.uid})
            if user is None:
                raise HTTPException(500, "utente non trovato")

            return AccountModel(**user).to_public()

    @classmethod
    async def restore_set(cls, key: str, newpassword: SecretStr) -> bool:

        # esegue di nuovo i controlli per la chiave
        user = await cls.restore_init(key)

        # esegui operazioni bcrypt in thread pool (CPU-intensive)
        ph = PasswordHasher()
        password_hash = await asyncio.to_thread(ph.hash, newpassword.get_secret_value())

        with MongoClient(MONGO_CS) as c:
            with c.start_session() as s:
                with s.start_transaction():
                    res = (
                        c[DB].accounts.update_one(
                            {"uid": user["uid"]},
                            {"$set": {"passwordHash": password_hash}},
                            session=s,
                        )
                    ).modified_count
                    if res <= 0:
                        s.abort_transaction()
                        raise HTTPException(
                            500, "errore nell'impostazione della nuova password"
                        )

                    res = (
                        c[DB].account_actions_keys.update_one(
                            {"key": key},
                            {"$set": {"usedAt": datetime.now()}},
                            session=s,
                        )
                    ).modified_count
                    if res <= 0:
                        s.abort_transaction()
                        raise HTTPException(500, "errore aggiornamento della chiave")

                    return True

    @classmethod
    async def send_recover_email(cls, email: str, recover_key: str) -> bool:
        """
        manda la email con il codice di attivazione dell'account.

        Return boolean se la mail è stata invata
        """

        link = f"{cls.RECOVER_LINK}/{recover_key}"

        # leggi il template in modo asincrono
        template = await asyncio.to_thread(ET_PASSWORD_RECOVER.read_text)
        body = Template(template).substitute(RECOVER_LINK=link)

        # esegui l'invio email in thread pool (operazione I/O bloccante)
        def _send_email():
            try:
                config = DagMailConfig(**MAIL_CONFIG)
                with DagMail(config) as ms:
                    ms.set_sender(None)  # usa il sender di default configurato
                    ms.add_receiver(email)
                    ms.messageHTML(body, "Recupero password")
                    delivery = ms.send()
                    ic("invio email di attivazione", delivery)
                    return True if not delivery else False
            except Exception as e:
                ic(str(e))
                return False

        return await asyncio.to_thread(_send_email)
