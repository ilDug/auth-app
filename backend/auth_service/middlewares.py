from typing import Annotated, Callable
from fastapi import Depends
from .requests import authentication, user_id, permissions, authorization, is_admin


# restituisce i claims dell'utente
AuthClaims = Annotated[dict, Depends(authentication)]
"""restituisce i claims dell'utente"""

UserId = Annotated[str, Depends(user_id)]
"""restituisce l'id dell'utente"""

AuthPermissions = Annotated[str, Depends(permissions)]
"""restituisce i permessi dell'utente"""

AuthorizeFn = Annotated[Callable, Depends(authorization)]
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
