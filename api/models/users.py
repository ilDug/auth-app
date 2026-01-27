from typing import List
from pydantic import ConfigDict, EmailStr
from .mongo import MongoBase

# class UserModel(MongoBase):
#     """classe utente che mostra solo le proprietà pubbliche"""

#     model_config = ConfigDict(extra="ignore")

#     uid: UuidStr
#     username: str | None = None
#     email: EmailStr
#     active: bool = False
#     authorizations: List[str] = []
#     registration_date: datetime | None = None

############# --> sostituito da AccountModel.to_public() in account.py


class UserUpdateModel(MongoBase):
    """
    classe per l'aggiornamento dell'utente
    senza la possibilità di modificare

    - id
    - uid
    - data di registrazione
    """

    model_config = ConfigDict(extra="ignore")

    username: str | None = None
    email: EmailStr | None = None
    active: bool | None = None
    authorizations: List[str] | None = None
