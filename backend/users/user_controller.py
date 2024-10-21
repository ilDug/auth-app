from fastapi import HTTPException
from pymongo import MongoClient
from core.config import MONGO_CS, DB
from models import UserModel as User


class Users:

    @classmethod
    def items(cls) -> list[User]:
        """restituisce la lista degli utenti registrati"""

        with MongoClient(MONGO_CS) as c:
            cursor = c[DB].accounts.find()
            users = [User(**u) for u in cursor]
            return users

    @classmethod
    def load(cls, user_id) -> User:
        """restituisce un utente dal suo id"""

        with MongoClient(MONGO_CS) as c:
            cursor = c[DB].accounts.find_one({"uid": user_id})
            if not cursor:
                raise HTTPException(status_code=404, detail="User not found")
            return User(**cursor)

    @classmethod
    def remove(cls, user_id) -> int:
        """rimuove un utente dal suo id"""

        with MongoClient(MONGO_CS) as c:
            cursor = c[DB].accounts.delete_one({"uid": user_id})

            if not (x := cursor.deleted_count):
                raise HTTPException(status_code=404, detail="User not found")

            return x

    @classmethod
    def update(cls, user: User) -> User:
        """aggiorna un utente"""

        data = user.model_dump(exclude={"id", "uid", "registration_date"})

        with MongoClient(MONGO_CS) as c:
            cursor = c[DB].accounts.update_one(
                {"uid": user.uid},
                {"$set": data},
            )

            if not cursor:
                raise HTTPException(status_code=500, detail="Error updating user")

            return cls.load(user.uid)
