from fastapi import HTTPException
from pymongo import AsyncMongoClient
from core.config import MONGO_CS, DB
from models import AccountModel


class Users:
    """classe per la gestione degli utenti nel database MongoDB"""

    @classmethod
    async def items(cls) -> list[dict]:
        """restituisce la lista degli utenti registrati"""

        async with AsyncMongoClient(MONGO_CS) as c:
            cursor = await c[DB].accounts.find()
            users = [AccountModel(**u).to_public() for u in cursor]
            return users

    @classmethod
    async def load(cls, user_id) -> dict:
        """restituisce un utente dal suo id"""

        async with AsyncMongoClient(MONGO_CS) as c:
            cursor = await c[DB].accounts.find_one({"uid": user_id})
            if not cursor:
                raise HTTPException(status_code=404, detail="User not found")
            return AccountModel(**cursor).to_public()

    @classmethod
    async def remove(cls, user_id) -> int:
        """rimuove un utente dal suo id"""

        async with AsyncMongoClient(MONGO_CS) as c:
            cursor = await c[DB].accounts.delete_one({"uid": user_id})

            if not (x := cursor.deleted_count):
                raise HTTPException(status_code=404, detail="User not found")

            return x

    @classmethod
    async def update(cls, new_user: dict) -> dict:
        """aggiorna un utente"""

        sensitive_fields = set(
            "password_hash",
            "keychain",
            "registration_date",
            "registrationDate",
            "uid",
            "username",
            "email",
        )
        filtered_data = {k: v for k, v in new_user.items() if k not in sensitive_fields}

        async with AsyncMongoClient(MONGO_CS) as c:
            cursor = await c[DB].accounts.update_one(
                {"uid": new_user.uid},
                {"$set": filtered_data},
            )

            if not cursor:
                raise HTTPException(status_code=500, detail="Error updating user")

            return await cls.load(new_user.uid)
