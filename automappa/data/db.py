#!/usr/bin/env python

from sqlalchemy import create_engine, MetaData, Column, Float, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.reflection import Inspector
from contextlib import contextmanager

from automappa import settings

# Create the engine and session
engine = create_engine(
    url=settings.db.url,
    pool_size=settings.db.pool_size,
    pool_pre_ping=settings.db.pool_pre_ping,
)
metadata = MetaData()
metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


def check_table_exists(table_name: str) -> bool:
    inspector = Inspector.from_engine(engine)
    return table_name in inspector.get_table_names()


# Context manager for handling sessions
@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


Base = declarative_base()


class MarkersTable(Base):
    __tablename__ = "markers"

    contig = Column(String, primary_key=True)
    orf = Column(String)
    sacc = Column(String)
    sname = Column(String)
    score = Column(Float)
    cutoff = Column(Float)


class BinningTable(Base):
    __tablename__ = "binning"

    contig = Column(String, primary_key=True)
    cluster = Column(String)
    completeness = Column(Float)
    purity = Column(Float)
    coverage_stddev = Column(Float)
    gc_content_stddev = Column(Float)
    coverage = Column(Float)
    gc_content = Column(Float)
    length = Column(Integer)
    superkingdom = Column(String)
    phylum = Column(String)
    class_ = Column(String)
    order = Column(String)
    family = Column(String)
    genus = Column(String)
    species = Column(String)
    taxid = Column(Integer)
    x_1 = Column(Float)
    x_2 = Column(Float)


class MetagenomeTable(Base):
    __tablename__ = "metagenome"

    id = Column(String, primary_key=True)
    sequence = Column(String)
