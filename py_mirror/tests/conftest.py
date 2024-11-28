from typing import Any

from fastapi import FastAPI
import pytest

from py_mirror.app.api.main import get_api


# @pytest.fixture
# def anyio_backend() -> str:
#     return "anyio"


@pytest.fixture(scope="function", autouse=False)
def api() -> FastAPI:
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
