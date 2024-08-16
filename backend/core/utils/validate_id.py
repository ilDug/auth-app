from bson import ObjectId
from fastapi import HTTPException


def validate_id(_id: str):
    """funzione che valida il formato delll'id di mongodb. restituisce un errore 400 in caso la verifica non sia positiva"""

    if not ObjectId.is_valid(_id):
        print("invalid Object _id - DAG ERROR")
        raise HTTPException(400, "Object ID non corretto")
    else:
        pass


# vecchio metodo sostituito a Settembre 2023
# try:
#     ObjectId(_id)
# except Exception as e:
#     print("invalid Object _id - DAG ERROR")
#     raise HTTPException(400, "Object ID non corretto")
