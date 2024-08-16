# import hashlib
# from datetime import datetime
# from fastapi import HTTPException
# from pymongo import MongoClient
# from ..models import AccountModel, AccountActionKeyModel
from .account import Account

# from core.config import ACTIVATION_KEY_LENGTH, MONGO_CS, DB


# #############################################################################################
# #################  ACCOUNT ACTIVATION    ####################################################
# #############################################################################################


class AccountActivation(Account):
    pass


#     @classmethod
#     def activate(cls, key: str) -> bool:
#         """Attiva l'account"""
#         if not key or len(key) != ACTIVATION_KEY_LENGTH:
#             raise HTTPException(400, "invalid activation link")

#         with MongoClient(MONGO_CS) as c:
#             with c.start_session() as s:
#                 with s.start_transaction():
#                     activation = c[DB].account_actions_keys.find_one({"key": key})
#                     if activation is None:
#                         raise HTTPException(400, "chiave di attivazione inesistente")
#                     activation = AccountActionKeyModel(**activation)

#                     user = c[DB].accounts.find_one({"uid": str(activation.uid)})
#                     user = AccountModel(**user)
#                     if user.active:
#                         raise HTTPException(400, "utente già attivo")

#                     if activation.scope != cls.ACTIVATION_SCOPE:
#                         raise HTTPException(
#                             400,
#                             "la chiave fornita non e' adatta per l'attivazione dell'account",
#                         )

#                     res = (
#                         c[DB]
#                         .accounts.update_one(
#                             {"uid": str(activation.uid)}, {"$set": {"active": True}}
#                         )
#                         .modified_count
#                     )
#                     if res <= 0:
#                         raise HTTPException(
#                             500,
#                             str(
#                                 "Errore attivazione account (impossibile impostare lo stato). Prova più tardi"
#                             ),
#                         )

#                     res = (
#                         c[DB]
#                         .account_actions_keys.update_one(
#                             {"_id": activation.id},
#                             {"$set": {"used_at": datetime.now()}},
#                         )
#                         .modified_count
#                     )

#                     if res <= 0:
#                         raise HTTPException(
#                             500,
#                             str(
#                                 "Errore attivazione account (impossibile aggiornare la data di attivazione) Prova di nuovo più tardi."
#                             ),
#                         )
#                     return True

#     @classmethod
#     def resend_activation_email(cls, email_hash: str):
#         pass
#         with MongoClient(MONGO_CS) as c:
#             user: AccountModel = None
#             users = c[DB].accounts.find({})
#             for u in users:
#                 if email_hash == hashlib.md5(u["email"].encode()).hexdigest():
#                     user = AccountModel(**u)
#                     break

#             if user is None:
#                 raise HTTPException(
#                     400, "email non trovata, esegui prima la registrazione"
#                 )

#             if user.active:
#                 raise HTTPException(400, "utente già attivo")

#             activations = [
#                 a
#                 for a in c[DB]
#                 .account_actions_keys.find(
#                     {"uid": user.uid, "scope": cls.ACTIVATION_SCOPE}
#                 )
#                 .sort([("created_at", -1)])
#                 .limit(1)
#             ]
#             activation = AccountActionKeyModel(**activations[0])
#             return cls.send_activation_email(user.email, activation.key)
