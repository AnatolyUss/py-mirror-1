import os
from typing import Any

from dotenv import dotenv_values
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base

from sqlalchemy import MetaData


class DataSource:
    _instance: "DataSource" = None  # type: ignore

    def __new__(cls) -> "DataSource":
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self) -> None:
        self._env_vars: dict[str, str | Any] = (
            {**dotenv_values(".env"), **os.environ}
            if not hasattr(self, "_env_vars")
            else self._env_vars
        )

        self.declarative_base: Any = (
            self._get_declarative_base()
            if not hasattr(self, "declarative_base")
            else self.declarative_base
        )

        self.async_engine: AsyncEngine = (
            self._get_async_engine()
            if not hasattr(self, "async_engine")
            else self.async_engine
        )

    def _get_declarative_base(self) -> Any:
        schema = self._env_vars.get("POSTGRES_SCHEMA")
        metadata = MetaData(schema=schema)
        return declarative_base(metadata=metadata)

    def _get_async_engine(self) -> AsyncEngine:
        env = self._env_vars.get("ENV")
        user = self._env_vars.get("POSTGRES_USERNAME")
        password = self._env_vars.get("POSTGRES_PASSWORD")
        dbname = self._env_vars.get("POSTGRES_DATABASE_NAME")
        host = self._env_vars.get("POSTGRES_HOST")
        port = self._env_vars.get("POSTGRES_PORT")
        pool_size = int(str(self._env_vars.get("SQLALCHEMY_POOL_SIZE")))
        max_overflow = int(str(self._env_vars.get("SQLALCHEMY_MAX_OVERFLOW")))
        pool_timeout = int(str(self._env_vars.get("SQLALCHEMY_POOL_TIMEOUT")))
        pool_recycle = int(str(self._env_vars.get("SQLALCHEMY_POOL_RECYCLE")))
        pg_url = f"postgresql+asyncpg://{user}:{password}@/{dbname}?host={host}:{port}"

        return create_async_engine(
            pg_url,
            poolclass=AsyncAdaptedQueuePool,
            # Maximum number of connections in the pool.
            pool_size=pool_size,
            # Allow the pool to grow beyond the set size when necessary,
            # without having to set a large pool size upfront.
            max_overflow=max_overflow,
            # Timeout when acquiring a connection.
            pool_timeout=pool_timeout,
            # Recycle connections after 1 hour.
            pool_recycle=pool_recycle,
            # Enable SQL logging (for debugging purposes).
            echo=(env == "DEV"),
        )

    async def init_db(self) -> None:
        # !!!Note, the below "unused" import is presented due to essential side effect.
        import py_mirror.app.storage.pg.models

        async with self.async_engine.begin() as connection:
            await connection.run_sync(self.declarative_base.metadata.create_all)
