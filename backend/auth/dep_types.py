from typing import Annotated, Callable
from fastapi import Depends
from .dep_functions import (
    authentication_guard,
    authorization_fn,
    is_admin,
)

AuthenticationGuard = Annotated[bool, Depends(authentication_guard)]
"""verifica che l'utente sia autenticato"""

AuthorizeFn = Annotated[Callable, Depends(authorization_fn)]
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
"""verifica che il client abbia il permesso di admin"""
