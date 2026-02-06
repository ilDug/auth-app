from enum import Enum


class PERMISSIONS(Enum):
    BASIC = "basic"
    ADMIN = "admin"
    USER_ADMIN = "user_admin"  # can edit and remove user
