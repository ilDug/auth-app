from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    PlainSerializer,
    WithJsonSchema,
    Field,
)

from bson import ObjectId
from typing import Annotated


######################################
### PYDANTIC V2
######################################


def validate_object_id(id: any) -> ObjectId:
    if isinstance(id, ObjectId):
        return id
    if ObjectId.is_valid(id):
        return ObjectId(id)
    raise ValueError("Invalid ObjectId [DAG]")


Oid = Annotated[
    str | ObjectId | None,
    PlainSerializer(
        lambda oid: str(oid) if oid is not None else None,
        return_type=str,
        when_used="always",
    ),
    AfterValidator(validate_object_id),
    WithJsonSchema({type: "string"}, mode="serialization"),
    Field(None, validation_alias="_id"),
]
"""ObjectId di MongoDB - definizione del tipo, del validatore, con alias _id e del serializzatore che lo trasforma in stringa"""


class MongoModel(BaseModel):
    """classe base per i modelli MongoDB"""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        # json_encoders={
        # datetime: lambda dt: f"{dt.isoformat()}+00:00",
        # datetime: lambda dt: f"{dt:%Y-%m-%dT%H:%M:%S.%f%Z}+00:00",
        # UUID: lambda uuid: str(uuid),
        # },
    )

    id: Oid
    """ _id restituito dal database mongodb"""
