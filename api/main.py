import fastapi
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from datetime import datetime

from core.config import CORS
from core.middlewares import validation_exception_handler, http_rewrite_header_handler
from routers import auth_router, sign_router

# LOGGING SETUP
# ###########################################################
# import logging
from icecream import ic

ic.configureOutput(includeContext=True, prefix="DAG LOG | ")

# log_formatter = logging.Formatter(
#     fmt="%(asctime)s - DAG - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(log_formatter)
# # file_handler = logging.FileHandler("auth-app.log")
# # file_handler.setFormatter(log_formatter)
# logger = logging.getLogger("auth-app")
# logger.setLevel(logging.WARNING)
# logger.addHandler(console_handler)
# logger.addHandler(file_handler)
# ###########################################################


ic("Starting auth-app... ")


app = FastAPI(
    title="auth-app",
    version="1.3.0",
    description="Authentication and Authorization server backend",
)


# MIDDLEWARE
app.add_middleware(CORSMiddleware, **CORS)


#  EXCEPTION HANDLERS
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_rewrite_header_handler)

# ROUTERS
app.include_router(auth_router)
app.include_router(sign_router)

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


# @app.get("/upgrade")
# async def upgrade():
#     # aggiorna gliaccount aggiungendo le chiavi mancanti
#     updated_accounts = add_keys_to_all_accounts()
#     return {"updated_accounts": updated_accounts}
