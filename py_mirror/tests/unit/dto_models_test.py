from typing import cast, Any

from pydantic import ValidationError

from py_mirror.app.types import ModelDto


def test_model_dto_success(valid_model_dto_payload: dict[str, Any]) -> None:
    modelDto, validation_error = None, None

    try:
        modelDto = ModelDto(
            path=valid_model_dto_payload["path"],
            method=valid_model_dto_payload["method"],
            body=valid_model_dto_payload["body"],
            headers=valid_model_dto_payload["headers"],
            query_params=valid_model_dto_payload["query_params"],
        )
    except ValidationError as e:
        validation_error = e

    assert isinstance(modelDto, ModelDto)
    assert validation_error is None


def test_model_dto_wrong_method(model_dto_wrong_method: dict[str, Any]) -> None:
    modelDto, validation_error = None, None

    try:
        modelDto = ModelDto(
            path=model_dto_wrong_method["path"],
            method=model_dto_wrong_method["method"],
            body=model_dto_wrong_method["body"],
            headers=model_dto_wrong_method["headers"],
            query_params=model_dto_wrong_method["query_params"],
        )
    except ValidationError as e:
        validation_error = e

    assert modelDto is None
    error = cast(ValidationError, validation_error).errors()[0]
    assert (
        error["msg"]
        == "Input should be 'CONNECT', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT' or 'TRACE'"
    )
    assert error["loc"][0] == "method"
    assert error["input"] == "GEET"


def test_model_dto_type_mismatch(model_dto_type_mismatch: dict[str, Any]) -> None:
    modelDto, validation_error = None, None

    try:
        modelDto = ModelDto(
            path=model_dto_type_mismatch["path"],
            method=model_dto_type_mismatch["method"],
            body=model_dto_type_mismatch["body"],
            headers=model_dto_type_mismatch["headers"],
            query_params=model_dto_type_mismatch["query_params"],
        )
    except ValidationError as e:
        validation_error = e

    assert modelDto is None
    error = cast(ValidationError, validation_error).errors()[0]
    assert error["loc"][0] == "headers"
    assert error["loc"][1] == 1
    assert error["loc"][2] == "required"
    assert error["input"] == "required"
    assert error["msg"] == "Input should be a valid boolean, unable to interpret input"
