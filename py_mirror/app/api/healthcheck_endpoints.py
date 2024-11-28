import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from py_mirror.app.types import ResponseDto, ReadinessResponseDto
from py_mirror.app.storage.pg.data_source import DataSource as PgDataSource
from py_mirror.app.storage.redis.data_source import DataSource as RedisDataSource

healthcheck_router = APIRouter(prefix="/healthcheck", tags=["healthcheck"])


@healthcheck_router.get("/liveness")
async def liveness() -> JSONResponse:
    return JSONResponse(
        status_code=200, content=jsonable_encoder(ResponseDto(data="Ok", error=None))
    )


@healthcheck_router.get("/readiness")
async def readiness() -> JSONResponse:
    try:
        redis_response, pg_response = await asyncio.gather(
            RedisDataSource().ping(),
            PgDataSource().ping(),
        )

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                ReadinessResponseDto(pg=pg_response, redis=redis_response, error=None)
            ),
        )
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                ReadinessResponseDto(pg=None, redis=None, error=jsonable_encoder(ex))
            ),
        )
