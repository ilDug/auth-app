from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from client import AuthClaims

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def root(claims: AuthClaims):
    message = f"""
Test endpoint for client authentication and claims retrieval.
This endpoint is protected by the AuthenticationGuard middleware, which verifies that the client is authenticated and retrieves the client's claims.

The claims are then returned in the response, allowing you to verify that the authentication and claims retrieval are working correctly.

these claims are retrieved using the AuthClaims dependency, which is defined in the client middlewares and uses the auth_claims function to extract the claims from the client's authentication token.

Claims:

```
{claims}
```
    
"""
    return message
