import bcrypt
from string import Template
from email_validator import validate_email
from datetime import datetime, timedelta
from fastapi import HTTPException
from pymongo import MongoClient
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
    HOST,
)

# #############################################################################################
# #################  PASSWORD #################################################################
# #############################################################################################


class Password(Account):
    pass

    RECOVER_SCOPE = "recover_password"
    RECOVER_LINK = f"{HOST}/account/password/restore/init"

    @classmethod
    def recover(cls, email: str) -> bool:
        """genera una chiave di attivazione che permette di ripristinare la password. Restituisce la key via email"""

        # controlla se l'email è presente e se è di un formato valido
        if not email:
            raise HTTPException(400, "il campo email non è specificato")

        email = email.lower().strip()

        try:
            validate_email(email)
        except Exception as e:
            raise HTTPException(400, "indirizzo email non valido")

        with MongoClient(MONGO_CS) as c:

            # cerca l'utente nel database
            user = c[DB].accounts.find_one({"email": email})
            if user is None:
                raise HTTPException(400, "indirizzo email non presente nel database")
            user = AccountModel(**user)

            # crea  la chiave di attivazione esiste e controlla che non esista già nel database
            while True:
                recover_key = random_string(ACTIVATION_KEY_LENGTH)
                if c[DB].account_actions_keys.find_one({"key": recover_key}) is None:
                    break

            # inserisce la chiave nel database
            id = (
                c[DB]
                .account_actions_keys.insert_one(
                    {
                        "uid": user.uid,
                        "key": recover_key,
                        "created_at": datetime.now(),
                        "used_at": None,
                        "scope": cls.RECOVER_SCOPE,
                    }
                )
                .inserted_id
            )

            if id is None:
                raise HTTPException(500, "Errore creazione chiave di recupero")

            # manda l'email di recover password
            if not cls.send_recover_email(email, recover_key):
                raise HTTPException(
                    500, "Errore nell recupero della password,  prova più tardi"
                )
            else:
                return True

    @classmethod
    def restore_init(cls, key: str) -> str:
        """esegui i controlli della chiave e restituisce l'uid dell'utente per procedere con il set della password"""

        if not key or len(key) != ACTIVATION_KEY_LENGTH:
            raise HTTPException(
                400, "la richiesta non contiene la chiave di attivazione corretta"
            )

        with MongoClient(MONGO_CS) as c:
            r = c[DB].account_actions_keys.find_one({"key": key})
            if not r:
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

            return str(operation.uid)

    @classmethod
    def restore_set(cls, key: str, newpassword: str) -> bool:
        """imposta la nuova password,  @return BOOL"""

        if not newpassword:
            raise HTTPException(400, "la richiesta non contiene la password")

        if not key or len(key) != ACTIVATION_KEY_LENGTH:
            raise HTTPException(400, "invalid recover link")

        # esegue di nuovo i controlli per la chiave
        uid = cls.restore_init(key)
        if not uid:
            raise HTTPException(500, "identificativo dell'utente non trovato")

        with MongoClient(MONGO_CS) as c:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(newpassword.encode(), salt).decode()
            res = (
                c[DB]
                .accounts.update_one(
                    {"uid": uid}, {"$set": {"hashed_password": hashed_pw}}
                )
                .modified_count
            )
            if res <= 0:
                raise HTTPException(
                    500, "errore nell'impostazione della nuova password"
                )

            res = (
                c[DB]
                .account_actions_keys.update_one(
                    {"key": key}, {"$set": {"used_at": datetime.now()}}
                )
                .modified_count
            )
            if res <= 0:
                raise HTTPException(500, "errore aggiornamento della chiave")

            return True

    @classmethod
    def send_recover_email(cls, email: str, recover_key: str) -> bool:
        """manda la email con il codice di attivazione edell'account.
        @return boolean se la mail è stata invata"""

        link = f"{cls.RECOVER_LINK}/{recover_key}"
        template = ET_PASSWORD_RECOVER.read_text()
        body = Template(template).substitute(RECOVER_LINK=link)

        try:
            config = DagMailConfig(**MAIL_CONFIG)
            with DagMail(config) as ms:
                ms.add_receiver(email)
                ms.messageHTML(body, "Recupero password")
                ms.send()
                return True
        except Exception as e:
            print(str(e))
            return False
