from enum import Enum

# PERMISSIONS = [
#     "basic",
#     "admin",
#     "user_edit",  # can edit user data
#     "user_remove",  # can remove user
#     "user_admin",  # can edit and remove user
# ]


class PERMISSIONS(Enum):
    BASIC = "basic"
    ADMIN = "admin"
    USER_ADMIN = "user_admin"  # can edit and remove user
