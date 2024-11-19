from typing import Any

import pytest


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
