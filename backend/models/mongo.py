from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    GetCoreSchemaHandler,
    PlainSerializer,
    WithJsonSchema,
    field_serializer,
    Field,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from datetime import datetime
from bson import ObjectId
from uuid import UUID
from typing import Annotated, Any, Callable, Optional, Type


######################################
### PYDANTIC V2
######################################


# class ObjectIdField(str):
#     @classmethod
#     def __get_pydantic_core_schema__(
#         cls, _source_type: Any, _handler: Any
#     ) -> core_schema.CoreSchema:
#         object_id_schema = core_schema.chain_schema(
#             [
#                 core_schema.str_schema(),
#                 core_schema.no_info_plain_validator_function(cls.validate),
#             ]
#         )

#         return core_schema.json_or_python_schema(
#             json_schema=object_id_schema,
#             python_schema=core_schema.union_schema(
#                 [core_schema.is_instance_schema(ObjectId), object_id_schema]
#             ),
#             serialization=core_schema.plain_serializer_function_ser_schema(
#                 lambda x: str(x)
#             ),
#         )

#     @classmethod
#     def validate(cls, value):
#         if not ObjectId.is_valid(value):
#             raise ValueError("Invalid id DAG")

#         return ObjectId(value)

#  /////////////////////////////////////////////////////////////////////////////////////


class MongoModel(BaseModel):
    id: Annotated[str | ObjectId | None, Field(alias="_id", exclude=True)] = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        json_encoders={
            # datetime: lambda dt: f"{dt:%Y-%m-%dT%H:%M:%S.%f%Z}+00:00",
            # datetime: lambda dt: dt.isoformat(),
            datetime: lambda dt: f"{dt.isoformat()}+00:00",
            ObjectId: lambda oid: str(oid),
            UUID: lambda uuid: str(uuid),
        },
        arbitrary_types_allowed=True,
    )


######################################
### PYDANTIC V1
######################################
# class OId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid mongo objectid")
#         return ObjectId(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")


# class MongoModel(BaseModel):
#     # id: OId = Field(None, alias="_id")
#     class Config:
#         json_encoders = {
#             # datetime: lambda dt: f"{dt:%Y-%m-%dT%H:%M:%S.%f%Z}+00:00",
#             # datetime: lambda dt: dt.isoformat(),
#             datetime: lambda dt: f"{dt.isoformat()}+00:00",
#             ObjectId: lambda oid: str(oid),
#             UUID: lambda uuid: str(uuid),
#         }
#         extra = "allow"
#         populate_by_name = True
