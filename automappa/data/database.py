#!/usr/bin/env python
from typing import List
from sqlmodel import SQLModel, create_engine

from dash_extensions.enrich import RedisBackend, FileSystemBackend

from automappa import settings

# SQL DATABASE file
# sqlite_url = f"sqlite:///database.db"
# engine = create_engine(sqlite_url, echo=False)

# SQL in-memory
# sqlite_url = f"sqlite:///:memory:"
# engine = create_engine(sqlite_url, echo=False)

# POSTGRES DATABASE
engine = create_engine(
    url=settings.db.url,
    pool_size=settings.db.pool_size,
    pool_pre_ping=settings.db.pool_pre_ping,
)

redis_backend = RedisBackend(
    **dict(host=settings.redis.host, port=settings.redis.port, db=settings.redis.db),
    # password=settings.redis.password,
)
file_system_backend = FileSystemBackend(cache_dir=settings.server.root_upload_folder)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_table_names() -> List[str]:
    return SQLModel.metadata.tables.keys()


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
