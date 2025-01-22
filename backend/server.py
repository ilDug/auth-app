from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from datetime import datetime

#######################################################
# o delete for upgrading
from account.controllers import add_keys_to_all_accounts

#######################################################

from auth import auth_router
from core import validation_exception_handler, http_rewrite_header_handler
from core.config import CORS
from core.utils import fastapi_version

# IMPORT ROUTERS
from account import account_router
from users import user_router

# MAIN FASTAPI APP
app = FastAPI(
    title="DAG Auth service",
    description="Authentication and Authorization server",
    version="1.2.6",
    # root_path="/api/v1",
)

# MIDDLEWARE
app.add_middleware(CORSMiddleware, **CORS)


#  EXCEPTION HANDLERS
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_rewrite_header_handler)


# ROUTERS
app.include_router(account_router)
app.include_router(auth_router)
app.include_router(user_router)


#  STATIC FILES
# app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="static_media")


# MAIN ROUTE
@app.get("/", response_class=PlainTextResponse)
async def root():
    return f"""AUTH SERVER VERSION {app.version},
RUNNING ON FASTAPI {fastapi_version()}.
Server time: {datetime.now()} (isoformat: {datetime.now().isoformat()})
"""


# HEALTH CHECK for load balancer
@app.get("/health")
async def check():
    return True


@app.get("/upgrade")
async def upgrade():
    # aggiorna gliaccount aggiungendo le chiavi mancanti
    updated_accounts = add_keys_to_all_accounts()
    return {"updated_accounts": updated_accounts}
