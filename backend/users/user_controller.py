from fastapi import HTTPException
from pymongo import MongoClient
from core.config import MONGO_CS, DB


class Users:

    @classmethod
    def add_user(self, user):
        with MongoClient(MONGO_CS) as c:
            id = c[DB].users.insert_one(user).inserted_id
            if id is None:
                raise HTTPException(500, "Error inserting user")
            return id

    def get_users(self):
        pass
