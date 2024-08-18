from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr
from .mongo import MongoModel
from .uuid_str import UuidStr


class UserModel(MongoModel):
    """classe utente"""

    model_config = ConfigDict(extra="ignore")

    uid: UuidStr
    username: str | None = None
    email: EmailStr
    active: bool = False
    authorizations: List[str] = []
    registration_date: datetime | None = None
