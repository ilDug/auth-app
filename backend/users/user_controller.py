from fastapi import HTTPException
from pymongo import MongoClient
from core.config import MONGO_CS, DB
from models import UserModel as User


class Users:

    @classmethod
    def items(self):
        """restituisce la lista degli utenti registrati"""
        with MongoClient(MONGO_CS) as c:
            cursor = c[DB].accounts.find()
            users = [User(**u) for u in cursor]
            return users
