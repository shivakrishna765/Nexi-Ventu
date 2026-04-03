"""
base_types.py
-------------
Shared SQLAlchemy column types that work with BOTH SQLite (dev) and PostgreSQL (prod).
Import PortableUUID from here instead of using pgUUID directly in models.
"""
import uuid
from sqlalchemy import types
from sqlalchemy.dialects.postgresql import UUID as pgUUID


class PortableUUID(types.TypeDecorator):
    """
    UUID column that stores as CHAR(36) in SQLite and native UUID in PostgreSQL.
    This lets the same model code run in both environments without changes.
    """
    impl = types.CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(pgUUID(as_uuid=True))
        return dialect.type_descriptor(types.CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return uuid.UUID(str(value))
        except (ValueError, AttributeError):
            return value
