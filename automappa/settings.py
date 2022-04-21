#!/usr/bin/env python

import os
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
    docker_url: Optional[PostgresDsn]
    local_url: Optional[PostgresDsn]
    pool_size: Optional[int] = 3
    is_docker_service : bool = os.environ.get('PWD') == '/usr/src/app'

    class Config:
        env_file: str = "automappa/environment/db.env"
        env_file_encoding: str = "utf-8"

class RabbitmqSettings(BaseSettings):
    url: AmqpDsn
    class Config:
        env_file: str = "automappa/environment/rabbitmq.env"
        env_file_encoding: str = "utf-8"


class FlowerSettings(BaseSettings):
    backend_url: RedisDsn
    broker_url: AmqpDsn
    class Config:
        env_file: str = "automappa/environment/flower.env"
        env_file_encoding: str = "utf-8"

class ServerSettings(BaseSettings):
    """
    Settings of the application, used by workers and dashboard.
    """
    upload_folder_root: Path
    # Dash/Plotly
    debug: Optional[bool] = True
    class Config:
        """
        Meta configuration of the settings parser.
        """
        env_file = "automappa/environment/server.env"
        env_file_encoding = "utf-8"
        
server = ServerSettings()
db = DatabaseSettings()
flower = FlowerSettings()