#!/usr/bin/env python

from pathlib import Path
from typing import Optional
from pydantic import (
    BaseSettings,
    RedisDsn,
    PostgresDsn,
    AmqpDsn,
)

# For the pydantic docs for defining settings, also See:
# https://pydantic-docs.helpmanual.io/usage/settings/


class DatabaseSettings(BaseSettings):
    # TODO: Figure out how to make the url dynamic to docker_url or local_url based on
    # is_docker_service... e.g.
    # url: PostgresDsn = docker_url if is_docker_service else local_url
    url: PostgresDsn
    pool_size: Optional[int] = 3

    class Config:
        env_prefix: str = "POSTGRES_"
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"


class RabbitmqSettings(BaseSettings):
    url: AmqpDsn

    class Config:
        env_prefix: str = "RABBITMQ_"
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"


class CelerySettings(BaseSettings):
    backend_url: RedisDsn
    broker_url: AmqpDsn

    class Config:
        env_prefix: str = "CELERY_"
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"


class ServerSettings(BaseSettings):
    root_upload_folder: Path
    # Dash/Plotly
    debug: Optional[bool] = True

    class Config:
        env_prefix = "SERVER_"
        env_file: str = ".env"
        env_file_encoding = "utf-8"


server = ServerSettings()
db = DatabaseSettings()
database  = DatabaseSettings()
rabbitmq  = RabbitmqSettings()
celery = CelerySettings()
