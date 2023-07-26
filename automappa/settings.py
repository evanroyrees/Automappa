#!/usr/bin/env python

from pathlib import Path
from typing import Optional
from pydantic import (
    BaseSettings,
    HttpUrl,
    RedisDsn,
    PostgresDsn,
    AmqpDsn,
)

# For the pydantic docs for defining settings, also See:
# https://pydantic-docs.helpmanual.io/usage/settings/


class DatabaseSettings(BaseSettings):
    url: PostgresDsn
    pool_size: Optional[int] = 4
    pool_pre_ping: Optional[bool] = False

    class Config:
        env_prefix: str = "POSTGRES_"
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"


class RedisSettings(BaseSettings):
    host: str
    port: int
    db: int
    password: str

    class Config:
        env_prefix: str = "REDIS_BACKEND_"
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


class FlowerSettings(BaseSettings):
    broker_api_url: HttpUrl

    class Config:
        env_prefix: str = "FLOWER_"
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"


class ServerSettings(BaseSettings):
    root_upload_folder: Path
    # Dash/Plotly
    host: Optional[str] = "localhost"
    port: Optional[int] = 8050
    debug: Optional[bool] = True

    class Config:
        env_prefix = "SERVER_"
        env_file: str = ".env"
        env_file_encoding = "utf-8"


server = ServerSettings()
db = DatabaseSettings()
redis = RedisSettings()
database = DatabaseSettings()
rabbitmq = RabbitmqSettings()
celery = CelerySettings()
