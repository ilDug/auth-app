import hashlib
import asyncio
from datetime import datetime
from fastapi import HTTPException
from pymongo import AsyncMongoClient
from models import AccountModel, AccountActionKeyModel
from .account import Account

from core.config import ACTIVATION_KEY_LENGTH, MONGO_CS, DB


# #############################################################################################
# #################  ACCOUNT ACTIVATION    ####################################################
# #############################################################################################


class AccountActivation(Account):

    @classmethod
    async def activate(cls, key: str) -> bool:
        """Attiva l'account dell'utente utilizzando la chiave di attivazione fornita"""

        # verifica  che la chiave di attivazione sia  pressente e della giusta lunghezza
        if not key or len(key) != ACTIVATION_KEY_LENGTH:
            raise HTTPException(400, "invalid activation link")

        async with AsyncMongoClient(MONGO_CS) as c:
            async with c.start_session() as s:
                async with s.start_transaction():

                    #  cerca la chiave di attivazione nel database, se non presente solleva un'eccezione
                    #  in modo che solo chi ha ricevuto la chiave possa attivare l'account
                    activation = await c[DB].account_actions_keys.find_one({"key": key})
                    if activation is None:
                        raise HTTPException(400, "chiave di attivazione inesistente")
                    activation = AccountActionKeyModel(**activation)

                    #  cerca l'utente nel database,  utilizzando l'uid associato alla chiave di attivazione
                    user = await c[DB].accounts.find_one({"uid": str(activation.uid)})
                    user = AccountModel(**user)
                    if user.active:
                        raise HTTPException(400, "utente già attivo")

                    #  verifica che la chiave di attivazione sia stata generata per l'attivazione dell'account
                    #  confrontando lo scope della chiave con quello di attivazione
                    if activation.scope != cls.ACTIVATION_SCOPE:
                        raise HTTPException(
                            400,
                            "la chiave fornita non e' adatta per l'attivazione dell'account",
                        )

                    #  aaggiorna lo stato dell'account a attivo
                    res = (
                        await c[DB].accounts.update_one(
                            {"uid": str(activation.uid)}, {"$set": {"active": True}}
                        )
                    ).modified_count

                    # se non è stato possibile aggiornare lo stato dell'account solleva un'eccezione
                    if res <= 0:
                        raise HTTPException(
                            500,
                            str(
                                "Errore attivazione account (impossibile impostare lo stato). Prova più tardi"
                            ),
                        )

                    # aggiorna la data di utilizzo della chiave di attivazione in modo da non poterla riutilizzare  in futuro
                    res = (
                        await c[DB].account_actions_keys.update_one(
                            {"_id": activation.id},
                            {"$set": {"used_at": datetime.now()}},
                        )
                    ).modified_count

                    # se non è stato possibile aggiornare la data di utilizzo della chiave di attivazione solleva un'eccezione
                    if res <= 0:
                        raise HTTPException(
                            500,
                            str(
                                "Errore attivazione account (impossibile aggiornare la data di attivazione) Prova di nuovo più tardi."
                            ),
                        )

                    return True

    @classmethod
    async def resend_activation_email(cls, email_hash: str) -> bool:
        """Invia una nuova email di attivazione all'utente con l'email fornita sotto forma di hash"""

        async with AsyncMongoClient(MONGO_CS) as c:
            user: AccountModel = None

            # cerca l'utente nel database utilizzando l'hash dell'email,
            # confrontando l'hash con quello presente nel database
            users = await c[DB].accounts.find({}).to_list(None)

            # esegui l'hashing e il confronto in thread pool (operazione CPU-intensive)
            def find_user_by_hash():
                for u in users:
                    if email_hash == hashlib.md5(u["email"].encode()).hexdigest():
                        return AccountModel(**u)
                return None

            user = await asyncio.to_thread(find_user_by_hash)

            # se l'utente non è presente solleva un'eccezione
            if user is None:
                raise HTTPException(
                    400, "email non trovata, esegui prima la registrazione"
                )

            # se l'utente è già attivo solleva un'eccezione
            if user.active:
                raise HTTPException(400, "utente già attivo")

            # cerca l'ultima chiave di attivazione generata per l'utente
            activations = (
                await c[DB]
                .account_actions_keys.find(
                    {"uid": user.uid, "scope": cls.ACTIVATION_SCOPE}
                )
                .sort([("created_at", -1)])
                .limit(1)
                .to_list(1)
            )

            #  reinvia la chiave di attivazione all'utente,  con il metodo
            # send_activation_email della classe parent AccountActivation
            activation = AccountActionKeyModel(**activations[0])
            return await cls.send_activation_email(user.email, activation.key)
