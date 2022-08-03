#!/usr/bin/env python

from datetime import datetime
import logging
from pathlib import Path
from typing import List, Optional
import uuid
import pandas as pd

from Bio.SeqIO import SeqRecord
from Bio.Seq import Seq

from autometa.common.markers import load as load_markers
from autometa.common.utilities import calc_checksum
from autometa.common.metagenome import Metagenome

from automappa.db import engine, metadata
from automappa.settings import server

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def get_uploaded_datatables() -> List[str]:
    return list(metadata.tables.keys())


def get_uploaded_files_table() -> pd.DataFrame:
    df = pd.DataFrame()
    tables = [table for table in metadata.tables.keys() if "fileupload" in table]
    with engine.connect() as conn:
        if tables:
            df = pd.DataFrame([pd.read_sql(table, conn) for table in tables])
    return df


def get_table(table_name: str, index_col: Optional[str] = None) -> pd.DataFrame:
    if not engine.has_table(table_name):
        tables = metadata.tables.keys()
        raise ValueError(f"{table_name} not in database! available: {tables}")
    df = pd.read_sql(table_name, engine)
    if index_col:
        df = df.set_index(index_col)
    logger.debug(f"retrieved {table_name} datatable, shape: {df.shape}")
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
    # Construct table name
    checksum = calc_checksum(str(filepath)).split()[0]
    table_name = f"{checksum}-binning"
    # Read filepath contents
    df = pd.read_csv(filepath, sep="\t")
    # NOTE: table_name must not exceed maximum length of 63 characters
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.debug(f"Saved {df.shape[0]:,} contigs to postgres table: {table_name}")
    # MAG Refinement Data Store
    # TODO: Refactor this to move it out of store_binning(...)
    # Should be another celery task...
    # NOTE: MAG refinement columns are enumerated (1-indexed) and prepended with 'refinement_'
    if "cluster" not in df.columns:
        df["cluster"] = "unclustered"
    else:
        df["cluster"].fillna("unclustered", inplace=True)

    refine_cols = [
        col
        for col in df.columns
        if "refinement_" in col or "cluster" in col or "contig" in col
    ]
    refinement_table_name = table_name.replace("-binning", "-refinement")
    df[refine_cols].to_sql(
        refinement_table_name, engine, if_exists=if_exists, index=False
    )
    logger.debug(
        f"Saved refinements (shape={df[refine_cols].shape}) to postgres table: {refinement_table_name}"
    )
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
    return table_name


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


def file_to_db(
    filepath: Path,
    filetype: str,
    if_exists: str = "replace",
    rm_after_upload: bool = True,
) -> pd.DataFrame:
    """Store `filepath` to db table based on `filetype`

    Parameters
    ----------
    filepath : Path
        Path to uploaded file to be stored in db table
    filetype : str
        type of file to be stored
        choices include 'markers', 'metagenome', 'binning'

    Returns
    -------
    pd.DataFrame
        cols=[filetype, filename, filesize (MB), table_id, uploaded, timestamp]

    Raises
    ------
    ValueError
        `filetype` not in filetype store methods
    """
    bytes_size = filepath.stat().st_size
    filesize = convert_bytes(bytes_size, "MB")
    timestamp = filepath.stat().st_mtime
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    filetype_store_methods = {
        "markers": store_markers,
        "metagenome": store_metagenome,
        "binning": store_binning_main,
    }
    if filetype not in filetype_store_methods:
        raise ValueError(
            f"{filetype} not in filetype store methods {','.join(filetype_store_methods.keys())}"
        )
    store_method = filetype_store_methods[filetype]
    try:
        table_id = store_method(filepath, if_exists=if_exists)
        if rm_after_upload:
            # TODO: Should have some way to retrieve data if already uploaded to server...
            # ...but data ingestion fails for some reason...
            logger.debug(f"Removed upload: {filepath.name} from server")
            filepath.unlink(missing_ok=True)
    except Exception as err:
        logger.error(err)
        return pd.DataFrame()
    df = pd.DataFrame(
        [
            {
                "filetype": filetype,
                "filename": filepath.name,
                "filesize (MB)": filesize,
                "table_id": table_id,
                "uploaded": last_modified,
                "timestamp": timestamp,
            }
        ]
    )

    # Create table_name specific to uploaded file with the upload file metadata...
    # This should contain mapping to where the file contents are stored (i.e. table_id)
    table_name = f"{uuid.uuid4()}-fileupload"
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.debug(f"Saved {table_name} to db")
    return df


def validate_uploader(iscompleted: bool, filenames, upload_id) -> Path:
    """Ensure only one file was uploaded and create Path to uploaded file

    Parameters
    ----------
    iscompleted : bool
        Whether or not the upload has finished
    filenames : list
        list of filenames
    upload_id : uuid
        unique user id associated with upload

    Returns
    -------
    Path
        Server-side path to uploaded file

    Raises
    ------
    ValueError
        You may only upload one file at a time!
    """
    if not iscompleted:
        return
    if filenames is None:
        return
    if upload_id:
        root_folder = server.root_upload_folder / upload_id
    else:
        root_folder = server.root_upload_folder

    uploaded_files = []
    for filename in filenames:
        file = root_folder / filename
        uploaded_files.append(file)
    if len(uploaded_files) > 1:
        raise ValueError("You may only upload one file at a time!")
    return uploaded_files[0]


if __name__ == "__main__":
    pass
