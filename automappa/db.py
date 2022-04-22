#!/usr/bin/env python

from sqlalchemy import create_engine, MetaData

from automappa.settings import db

engine = create_engine(
    url=db.url,
    pool_size=db.pool_size,
    pool_pre_ping=db.pool_pre_ping,
)

metadata = MetaData(bind=engine)
