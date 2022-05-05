#!/usr/bin/env python

from sqlalchemy import create_engine, MetaData
# from sqlalchemy import create_engine, MetaData, Table
# from sqlalchemy import inspect

# User inspector for retrieving db info:
# Inspector: https://docs.sqlalchemy.org/en/14/core/reflection.html?highlight=inspector%20has_table#sqlalchemy.engine.reflection.Inspector
# has_table: https://docs.sqlalchemy.org/en/14/core/reflection.html?highlight=has_table#sqlalchemy.engine.reflection.Inspector.has_table

from automappa.settings import db

engine = create_engine(
    url=db.url,
    pool_size=db.pool_size,
    pool_pre_ping=db.pool_pre_ping,
)

metadata = MetaData(bind=engine)

# inspector = inspect(engine)
# user_table = Table('user', metadata)
# insp.reflect_table(user_table, None)