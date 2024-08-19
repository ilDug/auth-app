from fastapi import Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError

from icecream import ic

ic.configureOutput(includeContext=True)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """cattura tutti gli errori di validazione di pydantic"""
    errors = [f"{e['msg']} - {e['type']}: {' '.join(e['loc'])}" for e in exc.errors()]
    ic("catch DAG PYDANTIC ERROR...")
    return JSONResponse(
        content=jsonable_encoder({"error": errors[0]}),
        status_code=400,
        headers={"X-Error": errors[0]},
    )


async def http_rewrite_header_handler(req: Request, exc: HTTPException):
    """Cattura tutti gli errori per poi poterli restituire come status code nella Response del server"""
    ic("catch DAG HTTP ERROR...", exc.status_code, exc.detail)

    return JSONResponse(
        content=jsonable_encoder({"error": exc.detail}),
        status_code=exc.status_code,
        headers={"X-Error": str(exc.detail)},
    )


async def mongo_error_handler(req: Request, exc: PyMongoError):
    ic("catch MONGO ERROR (by DAG): ")

    return PlainTextResponse(
        content=str(exc), status_code=500, headers={"X-Error": str(exc)}
    )
