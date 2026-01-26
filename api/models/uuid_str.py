from typing import Annotated
import re
from pydantic import AfterValidator


def validate_uuid_str(uuid: str) -> str:
    """
    Validates that the given string is a properly formatted UUID.

    Args:
        uuid (str): The UUID string to validate.

    Returns:
        str: The validated UUID string.

    Raises:
        ValueError: If the UUID string does not have a length of 36 characters.
        ValueError: If the UUID string does not match the expected UUID format.
    """
    if len(uuid) != 36:
        raise ValueError("Invalid UUID length [DAG]")

    regex = re.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    if not regex.match(uuid):
        raise ValueError("Invalid UUID format [DAG]")

    return uuid


# This module provides a custom type `UuidStr` for validating UUID strings using Pydantic's `Annotated` and `AfterValidator`.
# UuidStr: A custom type for UUID strings that ensures the string is a valid UUID.
UuidStr = Annotated[str, AfterValidator(validate_uuid_str)]
