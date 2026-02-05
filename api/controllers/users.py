from fastapi import HTTPException
from pymongo import AsyncMongoClient
from core.config import MONGO_CS, DB
from models import AccountModel, UuidStr


class Users:
    """classe per la gestione degli utenti nel database MongoDB"""

    @classmethod
    async def items(cls) -> list[dict]:
        """restituisce la lista degli utenti registrati"""

        async with AsyncMongoClient(MONGO_CS) as c:
            users_data = await c[DB].accounts.find().to_list(length=None)
            users = [AccountModel(**u).to_public() for u in users_data]
            return users

    @classmethod
    async def load(cls, uid) -> dict:
        """restituisce un utente dal suo id"""

        async with AsyncMongoClient(MONGO_CS) as c:
            cursor = await c[DB].accounts.find_one({"uid": uid})
            if not cursor:
                raise HTTPException(status_code=404, detail="User not found")
            return AccountModel(**cursor).to_public()

    @classmethod
    async def remove(cls, uid) -> int:
        """rimuove un utente dal suo id"""

        async with AsyncMongoClient(MONGO_CS) as c:
            cursor = await c[DB].accounts.delete_one({"uid": uid})
            if not (x := cursor.deleted_count):
                raise HTTPException(status_code=404, detail="User not found")

            return x

    @classmethod
    async def update(cls, new_user: dict) -> dict:
        """aggiorna un utente"""

        print(f"Received update request for user: {new_user}")
        sensitive_fields = {
            "password_hash",
            "keychain",
            "registration_date",
            "registrationDate",
            "uid",
            "username",
            "email",
        }
        filtered_data = {k: v for k, v in new_user.items() if k not in sensitive_fields}

        uid: UuidStr = new_user.get("uid")
        if not uid:
            raise HTTPException(
                status_code=400, detail="User ID is required for update"
            )

        print(f"Updating user {uid} with data: {filtered_data}")

        async with AsyncMongoClient(MONGO_CS) as c:
            cursor = await c[DB].accounts.update_one(
                {"uid": uid},
                {"$set": filtered_data},
            )

            if not cursor.modified_count and not cursor.matched_count:
                raise HTTPException(status_code=500, detail="Error updating user")

            return await cls.load(uid)
