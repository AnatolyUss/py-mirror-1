import asyncio
from typing import Any

from fastapi import FastAPI
import pytest
import pytest_asyncio

from py_mirror.app.api.main import get_api


# @pytest.fixture(scope="session")
@pytest_asyncio.fixture(scope="session")
async def event_loop_policy() -> asyncio.unix_events._UnixDefaultEventLoopPolicy:
    return asyncio.DefaultEventLoopPolicy()


# @pytest.fixture(scope="session", autouse=False)
@pytest_asyncio.fixture(scope="session", autouse=False)
async def api() -> FastAPI:
    return get_api()


@pytest.fixture(scope="function", autouse=False)
def valid_model_dto_payload() -> dict[str, Any]:
    return {
        "path": "/resource1/id1",
        "method": "GET",
        "body": [],
        "query_params": [],
        "headers": [
            {
                "name": "Authorization",
                "required": True,
                "types": ["String"],
            },
            {
                "name": "Content-Type",
                "required": True,
                "types": ["String"],
            },
        ],
    }


@pytest.fixture(scope="function", autouse=False)
def model_dto_wrong_method() -> dict[str, Any]:
    return {
        "path": "/resource1/id1",
        "method": "GEET",
        "body": [],
        "query_params": [],
        "headers": [
            {
                "name": "Authorization",
                "required": True,
                "types": ["String"],
            },
            {
                "name": "Content-Type",
                "required": True,
                "types": ["String"],
            },
        ],
    }


@pytest.fixture(scope="function", autouse=False)
def model_dto_type_mismatch() -> dict[str, Any]:
    return {
        "path": "/resource1/id1",
        "method": "GET",
        "body": [],
        "query_params": [],
        "headers": [
            {
                "name": "Authorization",
                "required": True,
                "types": ["String"],
            },
            {
                "name": "Content-Type",
                "required": "required",
                "types": ["Int"],
            },
        ],
    }
