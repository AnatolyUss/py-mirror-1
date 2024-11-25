from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column,
    Index,
    Identity,
    BigInteger,
    String,
    Enum as PgEnum,
)

from py_mirror.app.types import HttpMethod
from py_mirror.app.storage.pg.data_source import DataSource


# Note, DataSource is a singleton, and get_declarative_base is always returns the same object.
# Hence, there is no issue to call the below statement multiple times.
Base = DataSource().declarative_base


class ModelEntity(Base):  # type: ignore
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
