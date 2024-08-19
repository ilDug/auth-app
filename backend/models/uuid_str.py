from typing import Annotated
import re
from pydantic import AfterValidator


def validate_uuid_str(uuid: str) -> str:
    if len(uuid) != 36:
        raise ValueError("Invalid UUID length [DAG]")

    regex = re.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    if not regex.match(uuid):
        raise ValueError("Invalid UUID format [DAG]")

    return uuid


UuidStr = Annotated[str, AfterValidator(validate_uuid_str)]
