from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from datetime import datetime

# IMPORT ROUTERS


# MAIN FASTAPI APP
app = FastAPI(root_path="/api")

# MIDDLEWARE
app.add_middleware(CORSMiddleware, **cors_mw_config)


#  EXCEPTION HANDLERS
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_rewrite_header_handler)


# ROUTERS
# app.include_router(account_router)


#  STATIC FILES
app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="static_media")


# MAIN ROUTE
@app.get("/", response_class=PlainTextResponse)
async def root():
    return f"""API SERVER RUNNING... FASTAPI {fastapi_version()}.
Server time: {datetime.now()} (isoformat: {datetime.now().isoformat() })
database: {DB} --- MongoDB user: {MONGO_USER}
"""
