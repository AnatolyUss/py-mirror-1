import os

from dotenv import dotenv_values
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

from sqlalchemy import (
    Column,
    Index,
    Identity,
    BigInteger,
    String,
    Enum as PgEnum,
    MetaData,
)

from py_mirror.app.types import HttpMethod

env = {**dotenv_values(".env"), **os.environ}

user = env.get("POSTGRES_USERNAME")
password = env.get("POSTGRES_PASSWORD")
dbname = env.get("POSTGRES_DATABASE_NAME")
host = env.get("POSTGRES_HOST")
port = env.get("POSTGRES_PORT")
schema = env.get("POSTGRES_SCHEMA")

metadata = MetaData(schema="public")
Base = declarative_base(metadata=metadata)
pg_url = f"postgresql+asyncpg://{user}:{password}@/{dbname}?host={host}:{port}"
async_engine = create_async_engine(pg_url, poolclass=AsyncAdaptedQueuePool)


class Model(Base):  # type: ignore
    __tablename__ = "models"

    id = Column(BigInteger, Identity(start=1), primary_key=True, nullable=False)
    path = Column(String(255), nullable=False)
    method = Column(PgEnum(HttpMethod), nullable=False)  # type: ignore
    body = Column(JSONB, nullable=False)
    headers = Column(JSONB, nullable=False)
    query_params = Column(JSONB, nullable=False)
    groups_to_names_units_map = Column(JSONB, nullable=False)
    groups_to_required_fields_map = Column(JSONB, nullable=False)

    __table_args__ = (Index("idx_models_path_method", "path", "method", unique=True),)


async def init_db() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
