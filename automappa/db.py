#!/usr/bin/env python

from sqlalchemy import create_engine

from automappa.settings import settings

engine = create_engine(
    url=settings.database_url,
    # pool_size=settings.database_pool_size,
    # pool_pre_ping=True,
)
