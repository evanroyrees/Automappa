#!/usr/bin/env python

import os
import logging
from pathlib import Path
from typing import List
import pandas as pd

from automappa.db import engine

from autometa.common.markers import load as load_markers
from autometa.common.utilities import calc_checksum
from autometa.common.metagenome import Metagenome

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def get_uploaded_datatables() -> List[str]:
    tables = engine.table_names()
    return tables


def get_datatable(table_name: str) -> pd.DataFrame:
    if not engine.has_table(table_name):
        tables = engine.table_names()
        raise ValueError(f"{table_name} not in postgres database! available: {tables}")
    df = pd.read_sql(table_name, engine).set_index("contig")
    logger.debug(f"retrieved {df.shape[0]} contigs from {table_name} datatable")
    return df


def convert_bytes(size: int, unit: str = "MB", ndigits: int = 2) -> float:
    """Convert bytes from os.path.getsize(...) to provided `unit`
    choices include: 'KB', 'MB' or 'GB'

    Parameters
    ----------
    size : int
        bytes returned from `os.path.getsize(...)`
    unit : str, optional
        size to convert from bytes, by default MB

    Returns
    -------
    float
        Converted bytes value
    """
    # Yoinked from
    # https://amiradata.com/python-get-file-size-in-kb-mb-or-gb/#Get_file_size_in_KiloBytes_MegaBytes_or_GigaBytes
    if unit == "KB":
        return round(size / 1024, ndigits)
    elif unit == "MB":
        return round(size / (1024 * 1024), ndigits)
    elif unit == "GB":
        return round(size / (1024 * 1024 * 1024), ndigits)
    else:
        return size


def store_binning_main(filepath: Path, if_exists: str = "replace") -> str:
    """Parse `filepath` into `pd.DataFrame` then save to postgres table

    `table_id` is composed of 2 pieces:

        1. md5 checksum of 'filepath'
        2. binning

        e.g. `'{checksum}-binning'`

    Parameters
    ----------
    filepath : Path
        Path to binning.main.tsv Autometa results
    if_exists : str
        {'fail', 'replace', 'append'}, by default 'replace'
        How to behave if the table already exists.

    Returns
    -------
    str
        table_id = postgres table id for retrieving stored data (AKA name of SQL table)
        e.g. `'{checksum}-binning'`
    """
    try:
        # Construct table name
        checksum = calc_checksum(str(filepath)).split()[0]
        table_name = f"{checksum}-binning"
        # Read filepath contents
        df = pd.read_csv(filepath, sep="\t")
        # NOTE: table_name must not exceed maximum length of 63 characters
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        logger.debug(f"Saved {df.shape[0]:,} contigs to postgres table: {table_name}")
    except Exception as err:
        logger.error(err)
        logger.error("There was an error processing this file.")
        table_name = ""

    return table_name


def store_markers(filepath: Path, if_exists: str = "replace") -> str:
    """Parse `filepath` into `pd.DataFrame` then save to postgres table

    `table_id` is composed of 2 pieces:

        1. md5 checksum of 'filepath'
        2. binning

        e.g. `'{checksum}-markers'`

    Parameters
    ----------
    filepath : Path
        Path to markers.tsv Autometa results
    if_exists : str
        {'fail', 'replace', 'append'}, by default 'replace'
        How to behave if the table already exists.

    Returns
    -------
    str
        table_id = postgres table id for retrieving stored data (AKA name of SQL table)
        e.g. `'{checksum}-markers'`
    """
    try:
        # Construct table name
        checksum = calc_checksum(str(filepath)).split()[0]
        table_name = f"{checksum}-markers"
        # Read filepath contents
        df = load_markers(filepath)
        # NOTE: table_name must not exceed maximum length of 63 characters
        df.to_sql(table_name, engine, if_exists=if_exists, index=True)
        logger.debug(
            f"Saved {df.shape[0]:,} contigs and {df.shape[1]:,} markers to postgres table: {table_name}"
        )
    except Exception as err:
        logger.error(err)
        logger.error("There was an error processing this file.")
        table_name = ""

    return table_name


def store_metagenome(filepath: Path, if_exists: str = "replace") -> str:
    """Parse `filepath` into `pd.DataFrame` then save to postgres table

    `table_id` is composed of 2 pieces:

        1. md5 checksum of 'filepath'
        2. metagenome

        e.g. `'{checksum}-metagenome'`

    Parameters
    ----------
    filepath : Path
        Path to metagenome.main.tsv Autometa results
    if_exists : str
        {'fail', 'replace', 'append'}, by default 'replace'
        How to behave if the table already exists.

    Returns
    -------
    str
        table_id = postgres table id for retrieving stored data (AKA name of SQL table)
        e.g. `'{checksum}-metagenome'`
    """
    try:
        # Read filepath contents
        logger.debug(f"{filepath} uploaded... converting for datatable...")
        metagenome = Metagenome(assembly=filepath)
        df = pd.DataFrame(
            [
                {"contig": seqrecord.id, "sequence": str(seqrecord.seq)}
                for seqrecord in metagenome.seqrecords
            ]
        )
        logger.debug(f"converted... saving to datatable...")
        # NOTE: table_name must not exceed maximum length of 63 characters
        # Construct table name
        checksum = calc_checksum(str(filepath)).split()[0]
        table_name = f"{checksum}-metagenome"
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        logger.debug(f"Saved {df.shape[0]:,} contigs to postgres table: {table_name}")
    except Exception as err:
        logger.error(err)
        logger.error("There was an error processing this file.")
        table_name = ""

    return table_name


if __name__ == "__main__":
    pass
