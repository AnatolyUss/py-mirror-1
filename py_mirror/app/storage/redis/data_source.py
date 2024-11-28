import os
from typing import Any

from dotenv import dotenv_values
import redis.asyncio as redis


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

        self.client: redis.Redis = (
            self._get_client() if not hasattr(self, "client") else self.client
        )

    def _get_client(self) -> redis.Redis:
        host = self._env_vars.get("REDIS_HOST")
        port = self._env_vars.get("REDIS_PORT")
        db = self._env_vars.get("REDIS_DB")
        pool_size = int(str(self._env_vars.get("REDIS_POOL_SIZE")))
        redis_url = f"redis://{host}:{port}/{db}"

        pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=pool_size,
            encoding="utf-8",
            decode_responses=True,
        )

        return redis.Redis.from_pool(pool)

    async def disconnect(self) -> None:
        await self.client.aclose(close_connection_pool=True)

    async def ping(self) -> str:
        result = await self.client.ping()
        return str(result)
