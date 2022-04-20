#!/usr/bin/env python

from pydantic import (
    BaseSettings,
    RedisDsn,
    PostgresDsn,
    AmqpDsn,
)

# Following:
# https://hackernoon.com/build-a-real-time-stock-price-dashboard-with-python-questdb-and-plotly
# https://github.com/gabor-boros/questdb-stock-market-dashboard/blob/main/app/settings.py

# For the pydantic docs for defining settings, also See:
# https://pydantic-docs.helpmanual.io/usage/settings/


class Settings(BaseSettings):
    """
    Settings of the application, used by workers and dashboard.
    """

    # Celery settings
    celery_broker: str = "redis://127.0.0.1:6379/0"

    # Database settings
    redis_dsn: RedisDsn = "redis://user:pass@localhost:6379/1"
    pg_dsn: PostgresDsn = "postgresql://admin:mypass@localhost:5432/automappa"
    amqp_dsn: AmqpDsn = "amqp://user:pass@localhost:5672/"
    database_pool_size: int = 3
    database_url = pg_dsn

    # Dash/Plotly
    debug: bool = True

    class Config:
        """
        Meta configuration of the settings parser.
        """

        case_sensitive = True
        # Prefix the environment variable not to mix up with other variables
        # used by the OS or other software.
        env_prefix = "AUTOMAPPA_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        fields = {
            "auth_key": {
                "env": "my_auth_key",
            },
            "redis_dsn": {"env": ["service_redis_dsn", "redis_url"]},
        }


settings = Settings()
