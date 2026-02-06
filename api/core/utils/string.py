import random
import string


def random_string(length: int = 64, _lower: bool = False) -> str:
    code = "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for _ in range(length)
    )
    return code.lower() if _lower else code
