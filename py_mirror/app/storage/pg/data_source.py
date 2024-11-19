import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

user = os.environ.get("POSTGRES_USERNAME")
password = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DATABASE_NAME")
host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("POSTGRES_PORT")
pg_url = f"postgresql+asyncpg://{user}:{password}@/{dbname}?host={host}:{port}"
engine = create_async_engine(pg_url, poolclass=AsyncAdaptedQueuePool)
