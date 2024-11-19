from enum import Enum
from typing import Final, Any

from pydantic import BaseModel, Field


class AbnormalityType(str, Enum):
    TYPE_MISSMATCH = "type_missmatch"
    REQUIRED_FIELD_MISSING = "required_field_missing"
    VALIDATION_TEMPLATE_MISSING = "validation_template_missing"


class Type(str, Enum):
    Int = "Int"
    String = "String"
    Boolean = "Boolean"
    List = "List"
    Date = "Date"
    Email = "Email"
    UUID = "UUID"
    Auth_Token = "Auth-Token"


class HttpMethod(str, Enum):
    CONNECT = "CONNECT"
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"


class ValidationUnitDto(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Validation unit name")
    value: Any = Field(description="Validation unit value")


class ValidationUnitTemplateDto(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Field name")
    required: bool
    types: list[Type]


class AbnormalityReason(BaseModel):
    type: AbnormalityType
    description: str


ValidationUnitTemplateName = str
AbnormalFieldName = str
RequiredFieldChecked = bool
AbnormalFields = dict[AbnormalFieldName, list[AbnormalityReason]]


class ValidationResponseDto(BaseModel):
    isAbnormal: bool = Field(
        default=False, description="Indicates if the field is abnormal"
    )
    abnormalFields: AbnormalFields = Field(default={}, description="Abnormal fields")


class ResponseDto(BaseModel):
    data: Any | None
    error: Any | None


class RequestModelDtoBase(BaseModel):
    path: str = Field(
        min_length=1,
        max_length=255,
        description="Path, which is a subject for incoming requests validation",
    )
    method: HttpMethod = Field(description="HTTP method")
    query_params: list[ValidationUnitTemplateDto]
    headers: list[ValidationUnitTemplateDto]
    body: list[ValidationUnitTemplateDto]


class RequestDto(RequestModelDtoBase):
    pass


class ModelDto(RequestModelDtoBase):
    # !!!Note, id is omitted on purpose.
    # Each value is a mapping of param names with their corresponding validation templates.
    groups_to_names_units_map: Final[
        dict[str, dict[ValidationUnitTemplateName, ValidationUnitTemplateDto]]
    ] = {"query_params": {}, "headers": {}, "body": {}}
    # Each value is a mapping of param names,
    # with their corresponding mapping of required field and boolean,
    # indicating if it was already checked.
    # Eventually, it helps to validate the "POST /request" input in O(n) time complexity.
    groups_to_required_fields_map: Final[
        dict[str, dict[ValidationUnitTemplateName, RequiredFieldChecked]]
    ] = {"query_params": {}, "headers": {}, "body": {}}
