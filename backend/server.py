from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import pydantic
from pymongo.errors import PyMongoError

from datetime import datetime
from os import environ as env
from core.utils import fastapi_version
from core.config import MONGO_USER, DB, ASSETS_PATH
from core.middleware import (
    cors_mw_config,
    http_rewrite_header_handler,
    mongo_error_handler,
    validation_exception_handler,
)

# IMPORT ROUTERS
from account.routers import account_router
from products.products_router import router as products_router
from warehouse.warehouse_router import router as warehouse_router
from orders.routers import promo_router, order_router, orders_router


from icecream import ic

ic.configureOutput(includeContext=True)


# MAIN FASTAPI APP
app = FastAPI(root_path="/api")

# MIDDLEWARE
app.add_middleware(CORSMiddleware, **cors_mw_config)


#  EXCEPTION HANDLERS
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_rewrite_header_handler)
app.add_exception_handler(PyMongoError, mongo_error_handler)


# ROUTERS
app.include_router(account_router)
app.include_router(products_router)
app.include_router(warehouse_router)
app.include_router(promo_router)
app.include_router(order_router)
app.include_router(orders_router)

#  STATIC FILES
app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="static_media")


# MAIN ROUTE
@app.get("/", response_class=PlainTextResponse)
async def root():
    return f"""API SERVER RUNNING... FASTAPI {fastapi_version()}.
Server time: {datetime.now()} (isoformat: {datetime.now().isoformat() })
database: {DB} --- MongoDB user: {MONGO_USER}
"""
