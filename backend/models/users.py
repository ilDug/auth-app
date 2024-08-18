from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr
from models import MongoModel


class UserModel(MongoModel):
    """classe utente"""

    model_config = ConfigDict(extra="ignore")

    uid: str
    username: str | None = None
    email: EmailStr
    active: bool = False
    authorizations: List[str] = []
    registration_date: datetime | None = None
