from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Table,
    Column,
    Identity,
    BigInteger,
    String,
    Enum as PgEnum,
)

from py_mirror.app.types import HttpMethod
from py_mirror.app.storage.pg.data_source import metadata


modelTable = Table(
    "model",
    metadata,
    Column("id", BigInteger, Identity(start=1), primary_key=True, nullable=False),
    Column("path", String(255), nullable=False),
    Column("method", PgEnum(HttpMethod), nullable=False),
    Column("body", JSONB, nullable=False),
    Column("headers", JSONB, nullable=False),
    Column("query_params", JSONB, nullable=False),
    Column("groups_to_names_units_map", JSONB, nullable=False),
    Column("groups_to_required_fields_map", JSONB, nullable=False),
)
