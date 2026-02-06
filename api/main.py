import fastapi
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from pymongo.errors import PyMongoError

from core.config import CORS
from core.middlewares import (
    validation_exception_handler,
    http_rewrite_header_handler,
    mongo_error_handler,
)
from routers import auth_router, sign_router, account_router, users_router

#############################################################
from icecream import ic

ic.configureOutput(includeContext=True, prefix=lambda: f"DAG LOG | {datetime.now().isoformat()} | ")
#############################################################

ic("Starting auth-app... ")


app = FastAPI(
    title="auth-app",
    version="2.0.3",
    description="Authentication and Authorization server backend",
)


# MIDDLEWARE
app.add_middleware(CORSMiddleware, **CORS)


#  EXCEPTION HANDLERS
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_rewrite_header_handler)
app.add_exception_handler(PyMongoError, mongo_error_handler)

# ROUTERS
app.include_router(auth_router)
app.include_router(sign_router)
app.include_router(account_router)
app.include_router(users_router)

#  STATIC FILES
# app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="static_media")

# MAIN ROUTE
@app.get("/", response_class=PlainTextResponse)
async def root():
    return f"""AUTH SERVER VERSION {app.version},
RUNNING ON FASTAPI {fastapi.__version__}.
Server time: {datetime.now()} (isoformat: {datetime.now().isoformat()})
"""


# HEALTH CHECK for load balancer
@app.get("/health")
async def check():
    return True