import json
import logging
import asyncio

import redis.asyncio as redis
from sqlalchemy import select, delete, update, RowMapping
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.sql.dml import Delete, Update

from py_mirror.app.types import ModelDto, ValidationUnitTemplateDto
from py_mirror.app.storage.pg.models import ModelEntity
from py_mirror.app.storage.pg.data_source import DataSource as PgDataSource
from py_mirror.app.storage.redis.data_source import DataSource as RedisDataSource


class ModelService:
    def __init__(self) -> None:
        self.redis_client: redis.Redis = RedisDataSource().client
        self.pg_session: async_sessionmaker[AsyncSession] = PgDataSource().async_session

    async def save_model(self, model_dto: ModelDto) -> None:
        # Arrange query params, headers and body as maps, prior saving.
        # Eventually it will speed up real - time requests validation,
        # due to reduced time complexity - "O(n)" instead of "O(n^2)".
        self.initialize_names_to_units_maps(model_dto)
        self.initialize_required_fields_map(model_dto)

        # !!!Note, asyncio.gather, when called with return_exceptions=True, never raises exceptions.
        pg_result, redis_result = await asyncio.gather(
            self.set_model_pg(model_dto),
            self.set_model_redis(model_dto),
            return_exceptions=True,
        )
        pg_update_failed = isinstance(pg_result, Exception)
        redis_update_failed = isinstance(redis_result, Exception)

        if not pg_update_failed and not redis_update_failed:
            # Successfully saved the model in both MongoDB and Redis.
            return

        # Attempt rollback changes, following failed "transaction".
        mode_delete = True

        if pg_update_failed and redis_update_failed:
            # NO NEED to revert any operation, since both failed.
            # Just throw an Error after rest of checks.
            pass
        elif pg_update_failed:
            await self.set_model_redis(model_dto, mode_delete)
        elif redis_update_failed:
            await self.set_model_pg(model_dto, mode_delete)

        # Notify the consumer, that current operation has failed.
        raise Exception(f"Failed to save the model {model_dto}")

    async def get_model(self, path: str, method: str) -> ModelDto | None:
        # In most cases, requested model will be found in Redis.
        model_dto = await self.get_model_redis(path, method)

        if model_dto:
            # Requested model was found in Redis.
            return model_dto

        # The model might be missing due to possible failure during model upload,
        # or, for example, due to Redis instance crash.
        # Try to find the model in PG.
        model_dto = await self.get_model_pg(path, method)

        if not model_dto:
            # Requested model not found in both Redis and PG.
            return None

        # Requested model was found in PG.
        # Save it in Redis prior returning to the consumer.
        await self.set_model_redis(model_dto)
        return model_dto

    def initialize_names_to_units_maps(self, model_dto: ModelDto) -> None:
        for field in model_dto.groups_to_names_units_map:
            # 'query_params', 'headers' and 'body'.
            names_to_units = model_dto.groups_to_names_units_map[field]
            templates = model_dto[field]

            for template in templates:
                names_to_units[template.name] = template

    def initialize_required_fields_map(self, model_dto: ModelDto) -> None:
        for field in model_dto.groups_to_required_fields_map:
            # 'query_params', 'headers' and 'body'.
            required_fields = model_dto.groups_to_required_fields_map[field]
            templates = model_dto[field]

            for template in templates:
                if template.required:
                    # False - means "initially unchecked" required field.
                    required_fields[template.name] = False

    async def get_model_pg(self, path: str, method: str) -> ModelDto | None:
        try:
            async with self.pg_session() as async_session:
                stmt = select(ModelEntity).where(
                    ModelEntity.path == path, ModelEntity.method == method
                )
                result = await async_session.execute(stmt)
                raw_model = result.mappings().fetchone()
                return self.parse_model_pg(raw_model) if raw_model else None
        except Exception as ex:
            logging.error(msg=repr(ex))
            raise

    async def set_model_pg(
        self, model_dto: ModelDto, mode_delete: bool = False
    ) -> None:
        try:
            async with self.pg_session() as async_session:
                stmt: Delete | Update = (
                    delete(ModelEntity)
                    if mode_delete
                    else update(ModelEntity).values(**model_dto)
                ).where(
                    ModelEntity.path == model_dto.path,
                    ModelEntity.method == model_dto.method,
                )

                await async_session.execute(stmt)
                await async_session.commit()
        except Exception as ex:
            logging.error(msg=repr(ex))
            raise

    async def set_model_redis(
        self, model_dto: ModelDto, mode_delete: bool = False
    ) -> None:
        try:
            key = self.get_key(model_dto.path, model_dto.method)

            if mode_delete:
                await self.redis_client.getdel(key)
            else:
                await self.redis_client.set(key, self.serialize_model_redis(model_dto))
        except Exception as ex:
            logging.error(msg=repr(ex))
            raise

    async def get_model_redis(self, path: str, method: str) -> ModelDto | None:
        try:
            key = self.get_key(path, method)
            serialized_model = await self.redis_client.get(key)
            return (
                self.parse_model_redis(serialized_model) if serialized_model else None
            )
        except Exception as ex:
            logging.error(msg=repr(ex))
            raise

    def get_key(self, path: str, method: str) -> str:
        return f"{path}:{method}"

    def serialize_model_redis(self, model_dto: ModelDto) -> str:
        return json.dumps(model_dto)

    def parse_model_redis(self, serialized_model: str) -> ModelDto:
        return ModelDto(**json.loads(serialized_model))

    def parse_model_pg(self, raw_model: RowMapping) -> ModelDto:
        return ModelDto(**raw_model)
