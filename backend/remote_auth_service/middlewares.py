from typing import Annotated, Callable
from fastapi import Depends
from .functions import (
    authentication_request,
    authentication_guard,
    authorization_request,
    get_user_id,
    get_permissions,
    is_admin,
)

AuthenticationGuard = Annotated[bool, Depends(authentication_guard)]
"""verifica che l'utente sia autenticato"""

# restituisce i claims dell'utente
AuthClaims = Annotated[dict, Depends(authentication_request)]
"""restituisce i claims dell'utente"""

UserId = Annotated[str, Depends(get_user_id)]
"""restituisce l'id dell'utente"""

AuthPermissions = Annotated[str, Depends(get_permissions)]
"""restituisce i permessi dell'utente"""

AuthorizeFn = Annotated[Callable, Depends(authorization_request)]
"""
restituisce una funzione che permette di verificare se il client possiede il permesso passat come argomento. Se non c'è il permesso, la funzione raise an Exception.

EXAMPLE

```python
@router.get("/my/endpoint")
async def my_function_with_permission(is_authorized: AuthorizeFn):
    authorized = await is_authorized("admin")
    ... 
    return ...
```
"""

IsAdmin = Annotated[bool, Depends(is_admin)]
"""verifica che \il client abbia il permesso di admin"""
