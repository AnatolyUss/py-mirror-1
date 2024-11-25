from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from py_mirror.app.types import ResponseDto

healthcheck_router = APIRouter(prefix="/healthcheck", tags=["healthcheck"])


@healthcheck_router.get("/liveness")
async def liveness() -> JSONResponse:
    return JSONResponse(
        status_code=200, content=jsonable_encoder(ResponseDto(data="Ok", error=None))
    )


@healthcheck_router.get("/readiness")
async def readiness() -> JSONResponse:
    return JSONResponse(
        status_code=200, content=jsonable_encoder(ResponseDto(data="Ok", error=None))
    )
