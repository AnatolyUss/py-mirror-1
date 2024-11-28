import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from py_mirror.app.types import ModelDto, RequestDto, ResponseDto
from py_mirror.app.service.model_service import ModelService
from py_mirror.app.service.request_service import RequestService

api_router = APIRouter(prefix="/api", tags=["request-model"])


@api_router.post("/request")
async def post_request(request_dto: RequestDto) -> JSONResponse:
    try:
        model_service = ModelService()
        model_dto = await model_service.get_model(request_dto.path, request_dto.method)

        if not model_dto:
            msg = f"Model not found for path:method '{request_dto.path}:{request_dto.method}'"
            raise HTTPException(
                status_code=404,
                detail=jsonable_encoder(ResponseDto(data=None, error=msg)),
            )

        request_service = RequestService()
        validation_response = request_service.validate_request(request_dto, model_dto)
        return JSONResponse(
            status_code=201,
            content=jsonable_encoder(ResponseDto(data=validation_response, error=None)),
        )
    except Exception as ex:
        logging.error(msg=repr(ex))
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                ResponseDto(data=None, error="POST /api/request Error occurred")
            ),
        )


@api_router.post("/model")
async def post_model(model_dto: ModelDto) -> JSONResponse:
    try:
        service = ModelService()
        await service.save_model(model_dto)
        return JSONResponse(
            status_code=201,
            content=jsonable_encoder(ResponseDto(data="Ok", error=None)),
        )
    except Exception as ex:
        logging.error(msg=repr(ex))
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                ResponseDto(data=None, error="POST /api/model Error occurred")
            ),
        )
