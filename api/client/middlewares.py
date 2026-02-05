from typing import Annotated
from fastapi import Depends
from .auth_fn import (
    auth_claims,
    get_user_id,
    get_permissions,
    is_authenticated,
    is_admin,
    get_email,
)

AuthenticationGuard = Annotated[bool, Depends(is_authenticated)]
"""verifica che l'utente sia autenticato"""

# restituisce i claims dell'utente
AuthClaims = Annotated[dict, Depends(auth_claims)]
"""restituisce i claims dell'utente"""

UserId = Annotated[str, Depends(get_user_id)]
"""restituisce l'id dell'utente"""

UserEmail = Annotated[str, Depends(get_email)]
"""restituisce l'email dell'utente"""

AuthPermissions = Annotated[list, Depends(get_permissions)]
"""restituisce i permessi dell'utente"""

IsAdmin = Annotated[bool, Depends(is_admin)]
"""verifica che il client abbia il permesso di admin"""
