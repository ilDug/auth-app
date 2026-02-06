from typing import Annotated
from fastapi import Depends
from .auth_fn import (
    authentication_guard,
    get_permissions,
    get_email,
    is_admin,
    get_token_claims,
    get_uid,
    get_account,
)
from models import AccountModel

AuthenticationGuard = Annotated[bool, Depends(authentication_guard)]
"""verifica che l'utente sia autenticato"""

IsAdmin = Annotated[bool, Depends(is_admin)]
"""verifica che il client abbia il permesso di admin"""

AuthenticatedUser = Annotated[AccountModel, Depends(get_account)]
"""restituisce l'account model se autenticato"""

TokenClaims = Annotated[dict, Depends(get_token_claims)]
"""restituisce i claims del token"""

Uid = Annotated[str, Depends(get_uid)]
"""restituisce l'uid dell'utente"""

UserEmail = Annotated[str, Depends(get_email)]
"""restituisce l'email dell'utente"""

AuthPermissions = Annotated[list[str], Depends(get_permissions)]
"""restituisce la lista dei permessi dell'utente"""
