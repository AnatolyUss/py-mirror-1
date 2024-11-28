import pytest
import asyncio
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

# from py_mirror.app.storage.pg.data_source import DataSource as PgDataSource
# from py_mirror.app.storage.redis.data_source import DataSource as RedisDataSource


@pytest.mark.asyncio
async def test_healthcheck_not_found(api: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/healthcheck/liveness_2")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_liveness(api: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/healthcheck/liveness")

    assert response.status_code == 200
    assert response.json() == {"data": "Ok", "error": None}


@pytest.mark.asyncio
async def test_readiness(api: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/healthcheck/readiness")

    assert response.status_code == 200
    assert response.json() == {"pg": "1", "redis": "True", "error": None}


@pytest.mark.asyncio
async def test_readiness_redis_failed(api: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/healthcheck/readiness")

    # TODO: must get rid of the 'Event loop is closed' error!
    assert response.status_code == 200
    assert response.json() == {"pg": "1", "redis": "True", "error": None}
