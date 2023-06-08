#!/usr/bin/env python

import logging
import uuid
import pandas as pd

from datetime import datetime
from functools import partial
from pathlib import Path
from typing import List, Optional

from Bio.SeqIO import SeqRecord
from Bio.Seq import Seq

from automappa.data.db import engine, metadata
from automappa.settings import server


logger = logging.getLogger(__name__)


def get_uploaded_datatables() -> List[str]:
    return list(metadata.tables.keys())


def get_table(table_name: str, index_col: Optional[str] = None) -> pd.DataFrame:
    if not inspector.has_table(table_name):
        tables = inspector.get_table_names()
        raise ValueError(f"{table_name} not in database! available: {tables}")
    df = pd.read_sql(table_name, engine)
    if index_col:
        df = df.set_index(index_col)
    logger.debug(f"retrieved {table_name} datatable, shape: {df.shape}")
    return df


def get_metagenome_seqrecords(table_name) -> List[SeqRecord]:
    df = get_table(table_name)
    return [
        SeqRecord(seq=Seq(record[1]), id=record[0], name=record[0])
        for record in df.to_records(index=False)
    ]


def table_to_db(
    df: pd.DataFrame, name: str, if_exists: str = "replace", index: bool = False
) -> None:
    """Write `df` to `table_name` in database.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of data to write
    name : str
        Name of data table to store in database
    if_exists : str, optional
        What to do if `name` exists.
        Choices include: 'fail', 'replace', 'append', by default "replace"
    index : bool, optional
        Whether to write the index to the database, by default False

    Returns
    -------
    NoneType
        Nothing is returned...
    """
    return df.to_sql(name=name, con=engine, if_exists=if_exists, index=index)


if __name__ == "__main__":
    pass
