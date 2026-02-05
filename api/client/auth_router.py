import httpx
from .endpoints import AUTH_SERVER_URL, CA_CERT_PATH
from fastapi import APIRouter, Request, HTTPException

router = APIRouter(tags=["auth"])


# ACCOUNT ROUTES
@router.post("/account/login")
@router.post("/account/register")
@router.get("/account/exists/{email_md5_hash}")
@router.get("/account/activate/{key}")
@router.get("/account/resend-activation/{email_md5_hash}")
@router.post("/account/password/recover")
@router.get("/account/password/restore/init/{key}")
@router.post("/account/password/restore/set")
# AUTH ROUTES
@router.get("/auth/authenticate")
@router.get("/auth/authorize")
@router.post("/auth/sign")
@router.post("/auth/verify_signature")
# USER ROUTES
@router.get("/users")
@router.get("/users/{user_id}")
@router.put("/users")
@router.delete("/users/{user_id}")
async def redirect_auth(req: Request):
    try:
        async with httpx.AsyncClient(verify=CA_CERT_PATH) as client:
            response = await client.get(
                f"{AUTH_SERVER_URL}{req.url.path}",
                headers=req.headers,
                cookies=req.cookies,
                params=req.query_params,
            )
            if response.status_code != 200:
                raise HTTPException(response.status_code, response.headers["x-error"])
            return response.json()

    # deal with connection errors
    except httpx.ConnectError as e:
        print(e)
        raise HTTPException(500, "Errore di connessione con Auth Server")

    # deal with timout errors
    except httpx.TimeoutException as e:
        print(e)
        raise HTTPException(504, "Timeout: il server non risponde")

    # deal wiht HTTP errors
    except httpx.HTTPStatusError as e:
        print(e)
        raise HTTPException(500, "HTTPX: Errore HTTP")

    # deal with Auth Errors from remote auth service
    except Exception as e:
        print(e)
        raise HTTPException(e.status_code, e.detail)
