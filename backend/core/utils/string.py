import random
import string
from fastapi import HTTPException
from datetime import datetime


def random_string(length: int = 64, _lower: bool = False) -> str:
    code = "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for _ in range(length)
    )
    return code.lower() if _lower else code
