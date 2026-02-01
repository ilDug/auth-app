import asyncio
from fastapi import HTTPException
from pymongo import AsyncMongoClient
from core.config import MONGO_CS, DB
from core.utils import generate_crypto_keys, UserKeyChain


async def save_keys(uid: str, keychain: UserKeyChain):
    """salva la coppia di chiavi cryptografiche  nell'account utente"""

    # ritrova l'utente dal database in base al uid
    async with AsyncMongoClient(MONGO_CS) as c:
        user = await c[DB].accounts.find_one({"uid": uid})
        if user is None:
            raise HTTPException(404, "utente non trovato")

        # aggiorna l'utente con la nuova coppia di chiavi
        cursor = await c[DB].accounts.update_one(
            {"uid": uid},
            {"$set": {"keychain": keychain.model_dump()}},
        )

        if cursor.modified_count < 1:
            raise HTTPException(500, "errore salvataggio chiavi")


async def add_keys_to_all_accounts():
    """aggiunge la coppia di chiavi crittografiche a tutti gli account utente"""

    # ritrova tutti gli utenti dal database
    async with AsyncMongoClient(MONGO_CS) as c:
        users = await c[DB].accounts.find().to_list(None)
        counter = 0

        # per ogni utente
        for user in users:
            if "keychain" not in user:
                # genera la coppia di chiavi in thread pool (CPU-intensive)
                keychain = await asyncio.to_thread(generate_crypto_keys)

                # aggiorna l'utente con la nuova coppia di chiavi
                cursor = await c[DB].accounts.update_one(
                    {"uid": user["uid"]},
                    {"$set": {"keychain": keychain.model_dump()}},
                )

                # incrementa il contatore
                counter += cursor.modified_count

                if cursor.modified_count < 1:
                    raise HTTPException(500, "errore salvataggio chiavi")

    return counter
