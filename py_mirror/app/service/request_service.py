import uuid
import re
import logging
import datetime
from typing import Any, Callable

from py_mirror.app.types import (
    ModelDto,
    ValidationUnitDto,
    ValidationResponseDto,
    Type,
    AbnormalityType,
    AbnormalityReason,
    RequestDto,
)


class RequestService:
    def validate_request(
        self, request_dto: RequestDto, model_dto: ModelDto
    ) -> ValidationResponseDto:
        validation_response_dto = ValidationResponseDto()

        for group_name in model_dto.groups_to_names_units_map.keys():
            response = self.validate_params_group(group_name, request_dto, model_dto)

            if response.is_abnormal:
                validation_response_dto.is_abnormal = True

                for abnormal_field in response.abnormal_fields:
                    # Avoid possible override of fields with the same name,
                    # but from different groups ('query_params', 'headers' and 'body').
                    group_and_field = f"{group_name}:{abnormal_field}"
                    validation_response_dto.abnormal_fields[group_and_field] = (
                        response.abnormal_fields[abnormal_field]
                    )

        return validation_response_dto

    def validate_params_group(
        self, group_name: str, request_dto: RequestDto, model_dto: ModelDto
    ) -> ValidationResponseDto:
        # Currently, there are two main flows to validate params:
        # 1.
        # Run through "POST /request" input and validate against corresponding validation template.
        # Along the way, we can find fields, which don't have corresponding validation template - yet another anomaly.
        # 2.
        # Must make sure, that all the required fields actually appear in the "POST /request" input.
        validation_response_dto = ValidationResponseDto()

        # Note, group names are the same for both RequestDto and ModelDto.
        # Both DTOs were thoroughly validated prior being saved to Redis and Mongo.
        validation_units = request_dto[group_name]
        validation_unit_templates = model_dto.groups_to_names_units_map[group_name]

        for unit in validation_units:
            # Validation unit's template can be picked by name.
            # Note:
            # 1. Both the unit, and it's corresponding template, must share the name, validated using name's and request's DTOs.
            # 2. Query params, headers and body were prearranged as name-value maps prior saving.
            # 3. Some endpoints, received via "POST /request", may not have corresponding validation template.
            template = validation_unit_templates[unit.name]

            if not template:
                abnormality_reason = AbnormalityReason(
                    type=AbnormalityType.VALIDATION_TEMPLATE_MISSING,
                    description=f"Field {unit.name} missing validation template",
                )

                self.set_anomaly_details(
                    unit.name, validation_response_dto, abnormality_reason
                )
                continue

            if template.required:
                # Current validation unit (field from "POST /request" input) appears to be "required".
                # Mark corresponding field in "groups_to_required_fields_map" as true.
                model_dto.groups_to_required_fields_map[group_name][template.name] = (
                    True
                )

            self.validate_type(unit, template.types, validation_response_dto)

        self.add_missing_required_fields(group_name, model_dto, validation_response_dto)
        return validation_response_dto

    def add_missing_required_fields(
        self,
        group_name: str,
        model_dto: ModelDto,
        validation_response_dto: ValidationResponseDto,
    ) -> None:
        for field in model_dto.groups_to_required_fields_map[group_name]:
            if not model_dto.groups_to_required_fields_map[group_name][field]:
                abnormality_reason = AbnormalityReason(
                    type=AbnormalityType.REQUIRED_FIELD_MISSING,
                    description=f"Required field {field} is missing",
                )

                self.set_anomaly_details(
                    field, validation_response_dto, abnormality_reason
                )

    def validate_type(
        self,
        unit: ValidationUnitDto,
        allowed_types: list[Type],
        validation_response_dto: ValidationResponseDto,
    ) -> None:
        is_valid_value = any(
            self.is_value_of_type(type, unit.value) for type in allowed_types
        )

        if is_valid_value:
            return

        allowed_types_str = ",".join(allowed_types)
        abnormality_reason = AbnormalityReason(
            type=AbnormalityType.TYPE_MISSMATCH,
            description=f"Field {unit.name} must be of type[s] {allowed_types_str}",
        )

        self.set_anomaly_details(unit.name, validation_response_dto, abnormality_reason)

    def set_anomaly_details(
        self, field_name: str, dto: ValidationResponseDto, reason: AbnormalityReason
    ) -> None:
        dto.is_abnormal = True

        if field_name in dto.abnormal_fields:
            dto.abnormal_fields[field_name].append(reason)
        else:
            dto.abnormal_fields[field_name] = [reason]

    def is_value_of_type(self, type: Type, value: Any) -> bool:
        try:
            func: Callable[[Any], bool] = {
                Type.Auth_Token: self.is_auth_token,
                Type.Date: self.is_date,
                Type.UUID: self.is_uuid,
                Type.Email: self.is_email,
                Type.List: self.is_list,
                Type.Boolean: self.is_bool,
                Type.Int: self.is_int,
                Type.String: self.is_str,
            }[type]

            return func(value)
        except KeyError:
            logging.error(msg=f"Unexpected type {type}")
            return False

    def is_email(self, x: Any) -> bool:
        if not self.is_str(x):
            return False

        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, x))

    def is_date(self, x: Any) -> bool:
        # Expected format is a date-string, formatted as "dd-mm-yyyy".
        if not self.is_str(x):
            return False

        if len(x) != 10:
            return False

        try:
            day, month, year = x.split("-")
            datetime.date(int(year), int(month), int(day))
            return True
        except ValueError:
            return False

    def format_number(self, x: int) -> str:
        return f"0{x}" if x < 10 else str(x)

    def is_int(self, x: Any) -> bool:
        return isinstance(x, int)

    def is_str(self, x: Any) -> bool:
        return isinstance(x, str)

    def is_bool(self, x: Any) -> bool:
        return isinstance(x, bool)

    def is_list(self, x: Any) -> bool:
        return isinstance(x, list)

    def is_auth_token(self, x: Any) -> bool:
        return x.startswith("Bearer ") if self.is_str(x) else False

    def is_uuid(self, x: Any) -> bool:
        try:
            uuid.UUID(x, version=4)
            return True
        except ValueError:
            return False
