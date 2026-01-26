from pydantic import (
    BaseModel,
    ConfigDict,
    PlainSerializer,
    PlainValidator,
    WithJsonSchema,
    Field,
)
from pydantic.alias_generators import to_camel
from bson import ObjectId
from typing import Annotated, Any

######################################
### PYDANTIC V2
######################################


def validate_object_id(id: Any) -> ObjectId | None:
    """Valida e converte un valore in ObjectId di MongoDB."""
    if id is None:
        return None
    if isinstance(id, ObjectId):
        return id
    if isinstance(id, str) and ObjectId.is_valid(id):
        return ObjectId(id)
    raise ValueError("Invalid ObjectId [DAG]")


######################################


def serialize_object_id(value: Any) -> Any:
    """Serializza un ObjectId di MongoDB in stringa (se presente)."""
    if isinstance(value, ObjectId):
        return str(value)
    return value


######################################

Oid = Annotated[
    ObjectId | None,  # Tipo di dato effettivo
    PlainValidator(validate_object_id),  # Validatore personalizzato
    WithJsonSchema({"type": "string"}, mode="serialization"),
    PlainSerializer(
        serialize_object_id,
        return_type=str | None,
        when_used="json",
    ),  # Serializzatore personalizzato che converte in stringa quando si esporta in JSON
    Field(None, validation_alias="_id"),
]
"""ObjectId di MongoDB - definizione del tipo, del validatore, con alias _id e del serializzatore che lo trasforma in stringa"""

######################################


class MongoBase(BaseModel):
    """Base comune per tutti i documenti MongoDB.

    Gestisce in automatico la serializzazione degli ObjectId in stringa quando
    il modello viene convertito in JSON (es. risposta API).
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        arbitrary_types_allowed=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
    )

    id: Oid
    """ _id restituito dal database mongodb"""

    def db_dump(self, include_id: bool = False) -> dict:
        """Restituisce il dizionario del modello pronto per essere salvato su MongoDB. Il campo 'id' viene escluso di default."""
        exclude = set()
        if not include_id:
            exclude.add("id")
        return self.model_dump(exclude=exclude)
