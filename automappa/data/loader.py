#!/usr/bin/env python
# DataLoader for Autometa results ingestion
from datetime import datetime
import logging
from pathlib import Path
import uuid
import pandas as pd

from functools import partial, reduce
from typing import Callable, List, Literal, Optional

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from sqlmodel import Session, select, SQLModel

from autometa.common.utilities import calc_checksum

from autometa.common.markers import load as autometa_markers_loader
from automappa.data.schemas import ContigSchema, CytoscapeConnectionSchema, MarkerSchema

from automappa.settings import server
from automappa.data.database import (
    create_db_and_tables,
    engine,
    get_table_names,
)
from automappa.data.models import (
    Contig,
    Marker,
    Metagenome,
    CytoscapeConnection,
    Refinement,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
numba_logger = logging.getLogger("numba")
numba_logger.setLevel(logging.WARNING)
numba_logger.propagate = False
h5py_logger = logging.getLogger("h5py")
h5py_logger.setLevel(logging.WARNING)
h5py_logger.propagate = False


Preprocessor = Callable[[pd.DataFrame], pd.DataFrame]


def compose(*functions: Preprocessor) -> Preprocessor:
    return reduce(lambda f, g: lambda x: g(f(x)), functions)


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
    digit_rounder = partial(round, ndigits=ndigits)
    if unit == "KB":
        return digit_rounder(size / 1024)
    elif unit == "MB":
        return digit_rounder(size / (1024**2))
    elif unit == "GB":
        return digit_rounder(size / (1024**3))
    else:
        return size


def get_metagenome_seqrecords(table_name: str) -> List[SeqRecord]:
    df = get_table(table_name)
    return [
        SeqRecord(seq=Seq(record[1]), id=record[0], name=record[0])
        for record in df.to_records(index=False)
    ]


def store_markers(filepath: Path, if_exists: str = "replace") -> str:
    """Parse `filepath` into `MarkersData` and save to the `markers` table in the PostgreSQL database.

    `table_id` is composed of 2 pieces:
        1. md5 checksum of 'filepath'
        2. markers

    Parameters
    ----------
    filepath : Path
        Path to markers.tsv Autometa results
    if_exists : str, optional
        {'fail', 'replace', 'append'}, by default 'replace'
        How to behave if the table already exists.

    Returns
    -------
    str
        table_id = PostgreSQL table id for retrieving stored data (AKA name of SQL table)
        e.g. `'{checksum}-markers'`
    """
    # Construct table name
    checksum = calc_checksum(str(filepath)).split()[0]
    table_name = f"{checksum}-markers"
    # Read filepath contents and create MarkersData entries
    df = autometa_markers_loader(filepath)
    df.to_sql(table_name, engine, if_exists=if_exists)
    logger.debug(
        f"Saved {df.shape[0]:,} contigs containing markers to the markers table: {table_name}"
    )
    return table_name


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


def store_cytoscape(filepath: Path, if_exists: str = "replace") -> str:
    """Parse `filepath` into `pd.DataFrame` then save to postgres table

    `table_id` is composed of 2 pieces:

        1. md5 checksum of 'filepath'
        2. cytoscape connections table

        e.g. `'{checksum}-cytoscape'`

    Parameters
    ----------
    filepath : Path
        Path to cytoscape connections table
    if_exists : str
        {'fail', 'replace', 'append'}, by default 'replace'
        How to behave if the table already exists.

    Returns
    -------
    str
        table_id = postgres table id for retrieving stored data (AKA name of SQL table)
        e.g. `'{checksum}-cytoscape'`
    """
    # Read filepath contents
    logger.debug(f"{filepath} uploaded... reading to datatable...")
    df = pd.read_table(
        filepath,
        dtype={"node1": str, "interaction": int, "node2": str, "connections": int},
    )
    logger.debug(f"saving {filepath} to datatable...")
    # NOTE: table_name must not exceed maximum length of 63 characters
    # Construct table name
    checksum = calc_checksum(str(filepath)).split()[0]
    table_name = f"{checksum}-cytoscape"
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.debug(f"Saved {df.shape[0]:,} contigs to postgres table: {table_name}")
    return table_name


def file_to_db(
    filepath: Path,
    filetype: Literal["markers", "metagenome", "binning", "cytoscape"],
    if_exists: str = "replace",
) -> pd.DataFrame:
    """Store `filepath` to db table based on `filetype`

    Parameters
    ----------
    filepath : Path
        Path to uploaded file to be stored in db table
    filetype : str
        type of file to be stored
        choices include 'markers', 'metagenome', 'binning', "cytoscape"

    Returns
    -------
    pd.DataFrame
        cols=[filetype, filename, filesize (MB), table_id, uploaded, timestamp]

    Raises
    ------
    ValueError
        `filetype` not in filetype store methods
    """
    logger.debug(f"Saving {filepath} to db")
    bytes_size = filepath.stat().st_size
    filesize = convert_bytes(bytes_size, "MB")
    timestamp = filepath.stat().st_mtime
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    create_methods = {
        "markers": create_markers,
        "metagenome": create_metagenome,
        "binning": create_contigs,
        "cytoscape": create_cytoscape_connections,
    }
    if filetype not in create_methods:
        raise ValueError(
            f"{filetype} not in filetype create methods {','.join(create_methods.keys())}"
        )
    create_method = create_methods[filetype]
    try:
        create_method(filepath)
    except Exception as err:
        logger.error(err)
        return pd.DataFrame()
    finally:
        logger.debug(f"Removed upload: {filepath.name} from server")
        filepath.unlink(missing_ok=True)
    df = pd.DataFrame(
        [
            {
                "filename": filepath.name,
                "filetype": filetype,
                "filesize (MB)": filesize,
                # "table_id": table_id,
                "uploaded": last_modified,
                # "timestamp": timestamp,
            }
        ]
    )
    # Create table_name specific to uploaded file with the upload file metadata...
    # This should contain mapping to where the file contents are stored (i.e. table_id)
    table_name = f"{uuid.uuid4()}-fileupload"
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.debug(f"Saved {table_name} to db")
    return df


def validate_uploader(
    is_completed: bool, filenames: List[str], upload_id: uuid.UUID
) -> Path:
    """Ensure only one file was uploaded and create Path to uploaded file

    Parameters
    ----------
    is_completed : bool
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
    if not is_completed:
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


def get_uploaded_files_table() -> pd.DataFrame:
    df = pd.DataFrame()
    table_names = [name for name in get_table_names() if "fileupload" in name]
    if table_names:
        df = pd.DataFrame(
            [pd.read_sql(table_name, engine) for table_name in table_names]
        )
    return df


def in_table_names(table_name: str) -> bool:
    return table_name in get_table_names()


def get_table(table_name: str, index_col: Optional[str] = None) -> pd.DataFrame:
    if not in_table_names(table_name):
        raise ValueError(f"{table_name} not in database!")
    df = pd.read_sql(table_name, engine)
    if index_col:
        df = df.set_index(index_col)
    logger.debug(f"retrieved {table_name} datatable, shape: {df.shape}")
    return df


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


def df_to_sqlmodel(df: pd.DataFrame, model: SQLModel) -> List[SQLModel]:
    """Convert a pandas DataFrame into a a list of SQLModel objects."""
    objs = [model(**row) for row in df.to_dict("records")]
    return objs


def create_metagenome(
    name: str, fpath: Optional[str], contigs: Optional[List[Contig]]
) -> Metagenome:
    logger.info(f"Adding metagenome from {fpath} to db")
    if not contigs:
        contigs = [
            Contig(header=record.id, seq=str(record.seq))
            for record in SeqIO.parse(fpath, "fasta")
        ]
    else:
        # Need to ensure Seq column is in contigs otherwise add them
        merge_seq_column = partial(add_seq_column, seqrecord_df=contig_seq_df)
    metagenome = Metagenome(name=name, contigs=contigs)
    with Session(engine) as session:
        session.add(metagenome)
        session.commit()
        session.refresh(metagenome)
    return metagenome


def read_metagenome(metagenome_id: int) -> Metagenome:
    with Session(engine) as session:
        metagenomes = (
            session.exec(select(Metagenome))
            .where(Metagenome.id == metagenome_id)
            .first()
        )
    return metagenomes


def read_metagenomes() -> List[Metagenome]:
    with Session(engine) as session:
        metagenomes = session.exec(select(Metagenome)).all()
    return metagenomes


def read_metagenome_seqrecords() -> List[str]:
    with Session(engine) as session:
        metagenomes = session.exec(select(Metagenome.contigs)).all()
    return metagenomes


def update_metagenomes() -> None:
    raise NotImplemented


def delete_metagenomes() -> None:
    raise NotImplemented


def rename_class_column_to_klass(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={ContigSchema.CLASS: ContigSchema.KLASS})


def rename_contig_column_to_header(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={ContigSchema.CONTIG: ContigSchema.HEADER})


def add_seq_column(df: pd.DataFrame, seqrecord_df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(df, seqrecord_df, on=ContigSchema.HEADER, how="left")


def add_markers_column(df: pd.DataFrame, markers_list_df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(
        df,
        markers_list_df,
        left_on=ContigSchema.HEADER,
        right_on=MarkerSchema.CONTIG,
        how="left",
    )


def load_contigs(fpath: str) -> pd.DataFrame:
    logger.info(f"Loading contigs: {fpath}")
    return pd.read_table(
        fpath,
        dtype={
            ContigSchema.CONTIG: str,
            ContigSchema.CLUSTER: str,
            ContigSchema.COMPLETENESS: float,
            ContigSchema.PURITY: float,
            ContigSchema.COVERAGE_STDDEV: float,
            ContigSchema.GC_CONTENT_STDDEV: float,
            ContigSchema.COVERAGE: float,
            ContigSchema.GC_CONTENT: float,
            ContigSchema.LENGTH: int,
            ContigSchema.SUPERKINGDOM: str,
            ContigSchema.PHYLUM: str,
            ContigSchema.CLASS: str,
            ContigSchema.ORDER: str,
            ContigSchema.FAMILY: str,
            ContigSchema.GENUS: str,
            ContigSchema.SPECIES: str,
            ContigSchema.TAXID: int,
            ContigSchema.X_1: float,
            ContigSchema.X_2: float,
        },
    )


async def create_contigs(fpath: str, markers: Optional[List[Marker]]) -> None:
    logger.info(f"Adding binned contigs from {fpath} to db")
    raw_data = load_contigs(fpath)
    if markers:
        merge_markers_column = partial(add_markers_column, markers_list_df=markers)
        preprocessor = compose(
            rename_class_column_to_klass,
            rename_contig_column_to_header,
            merge_markers_column,
        )
    data = preprocessor(raw_data)
    contigs = df_to_sqlmodel(data, Contig)
    contig_df = preprocessor(raw_data)
    nonmarker_contigs_mask = contig_df.markers.isna()
    nonmarker_contigs = df_to_sqlmodel(
        contig_df.loc[nonmarker_contigs_mask].drop(columns=["markers"]), Contig
    )
    marker_contigs = df_to_sqlmodel(contig_df.loc[~nonmarker_contigs_mask], Contig)
    contigs = nonmarker_contigs + marker_contigs

    with Session(engine) as session:
        session.add_all(contigs)
        session.commit(contigs)
        session.refresh(contigs)
    await contigs


def read_contigs(headers: List[str] = []) -> List[Contig]:
    statement = select(Contig)
    if headers:
        statement = statement.where(Contig.header.in_(headers))
    with Session(engine) as session:
        contigs = session.exec(statement).all()
    return contigs


def update_contigs():
    raise NotImplemented


def delete_contig(contig: Contig) -> None:
    with Session(engine) as session:
        session.delete(contig)
        session.commit()


def rename_qname_column_to_orf(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={MarkerSchema.QNAME: MarkerSchema.ORF})


def drop_contig_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[MarkerSchema.CONTIG])


def agg_to_markers_list_column(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.set_index(MarkerSchema.CONTIG)
        .apply(func=lambda row: Marker(**row), axis=1, result_type="reduce", raw=False)
        .to_frame(name="markers")
        .reset_index()
        .groupby(MarkerSchema.CONTIG)
        .agg({"markers": lambda x: x.tolist()})
    )


def load_markers(fpath: str) -> pd.DataFrame:
    logger.info(f"Loading markers: {fpath}")
    return pd.read_table(
        fpath,
        usecols=[
            MarkerSchema.CONTIG,
            MarkerSchema.QNAME,
            MarkerSchema.SNAME,
            MarkerSchema.SACC,
            MarkerSchema.FULL_SEQ_SCORE,
            MarkerSchema.CUTOFF,
        ],
        dtype={
            MarkerSchema.CONTIG: str,
            MarkerSchema.QNAME: str,
            MarkerSchema.SNAME: str,
            MarkerSchema.SACC: str,
            MarkerSchema.FULL_SEQ_SCORE: float,
            MarkerSchema.CUTOFF: float,
        },
    )


async def create_markers(fpath: str) -> List[Marker]:
    logger.info(f"Adding markers from {fpath} to db")
    raw_data = load_markers(fpath)
    preprocessor = compose(rename_qname_column_to_orf, drop_contig_column)
    data = preprocessor(raw_data)
    markers = df_to_sqlmodel(data, Marker)
    with Session(engine) as session:
        session.add_all(markers)
        session.commit()
        session.refresh(markers)
    return markers


def read_markers(contig_headers: List[str] = None) -> List[Marker]:
    statement = select(Marker)
    if contig_headers:
        statement = statement.where(Marker.contig.header.in_(contig_headers))
    with Session(engine) as session:
        markers = session.exec(statement).all()
    return markers


def update_markers() -> None:
    raise NotImplemented


def delete_markers() -> None:
    raise NotImplemented


def load_cytoscape_connections(fpath: str) -> pd.DataFrame:
    logger.info(f"Loading cytoscape connections: {fpath}")
    return pd.read_table(
        fpath,
        low_memory=False,
        usecols=[
            CytoscapeConnectionSchema.NODE1,
            CytoscapeConnectionSchema.INTERACTION,
            CytoscapeConnectionSchema.NODE2,
            CytoscapeConnectionSchema.CONNECTIONS,
            CytoscapeConnectionSchema.MAPPINGTYPE,
            CytoscapeConnectionSchema.NAME,
            CytoscapeConnectionSchema.CONTIGLENGTH,
        ],
        dtype={
            CytoscapeConnectionSchema.NODE1: str,
            CytoscapeConnectionSchema.INTERACTION: int,
            CytoscapeConnectionSchema.NODE2: str,
            CytoscapeConnectionSchema.CONNECTIONS: int,
            CytoscapeConnectionSchema.MAPPINGTYPE: str,  # Literal['intra', 'ss', 'se', 'ee']
            # Below are commented as these are missing when mapping type != intra
            # causing pd.read_table(...) to fail...
            # CytoscapeConnectionSchema.NAME: str,
            # CytoscapeConnectionSchema.CONTIGLENGTH: int,
        },
    )


def create_cytoscape_connections(fpath: str) -> None:
    logger.info(f"Adding cytoscape connections from {fpath} to db")
    cyto_df = load_cytoscape_connections(fpath)
    cytoscape_connections = df_to_sqlmodel(cyto_df, CytoscapeConnection)
    with Session(engine) as session:
        session.add_all(cytoscape_connections)
        session.commit()


def read_cytoscape_connections() -> List[CytoscapeConnection]:
    logger.info("Reading cytoscape connections...")
    with Session(engine) as session:
        results = session.exec(select(CytoscapeConnection)).all()
    return results


def update_cytoscape_connection() -> None:
    raise NotImplemented


def delete_cytoscape_connection(connection: CytoscapeConnection) -> None:
    with Session(engine) as session:
        session.delete(connection)
        session.commit()


def create_sample_metagenome(
    name: str,
    metagenome_fpath: str,
    binning_fpath: str,
    markers_fpath: str,
    connections_fpath: Optional[str] = None,
) -> Metagenome:
    logger.info(f"Creating Metagenome {name=}")
    raw_markers = load_markers(markers_fpath)
    marker_preprocessor = compose(
        rename_qname_column_to_orf, agg_to_markers_list_column
    )
    contig_markers_df = marker_preprocessor(raw_markers)

    raw_binning = load_contigs(binning_fpath)
    contig_seq_df = pd.DataFrame(
        [
            dict(header=record.id, seq=str(record.seq))
            for record in SeqIO.parse(metagenome_fpath, "fasta")
        ]
    )
    merge_seq_column = partial(add_seq_column, seqrecord_df=contig_seq_df)
    merge_markers_column = partial(
        add_markers_column, markers_list_df=contig_markers_df
    )
    contig_preprocessor = compose(
        rename_class_column_to_klass,
        rename_contig_column_to_header,
        merge_seq_column,
        merge_markers_column,
    )
    contig_df = contig_preprocessor(raw_binning)
    nonmarker_contigs_mask = contig_df.markers.isna()
    nonmarker_contigs = df_to_sqlmodel(
        contig_df.loc[nonmarker_contigs_mask].drop(columns=["markers"]), Contig
    )
    marker_contigs = df_to_sqlmodel(contig_df.loc[~nonmarker_contigs_mask], Contig)
    contigs = nonmarker_contigs + marker_contigs
    # Add cytoscape connection mapping if available
    if connections_fpath:
        connections_df = load_cytoscape_connections(connections_fpath)
        connections = df_to_sqlmodel(connections_df, CytoscapeConnection)
    else:
        connections = []

    metagenome = Metagenome(
        name=name, contigs=contigs, connections=connections, refinements=[]
    )
    with Session(engine) as session:
        session.add(metagenome)
        session.commit()
        session.refresh(metagenome)
    return metagenome


def create_initial_refinements(metagenome_id: int) -> None:
    """Initialize Contig.refinements for contigs with Contig.cluster values

    Parameters
    ----------
    metagenome_id : int
        Metagenome.id value corresponding to Contigs
    """
    clusters_stmt = (
        select([Contig.cluster])
        .where(
            Contig.metagenome_id == metagenome_id,
            Contig.cluster != None,
            Contig.cluster != "nan",
        )
        .distinct()
    )
    with Session(engine) as session:
        clusters = session.exec(clusters_stmt).all()

        for cluster in clusters:
            contigs_in_cluster = session.exec(
                select(Contig).where(Contig.cluster == cluster)
            ).all()

            refinement = Refinement(
                contigs=contigs_in_cluster,
                outdated=False,
                initial_refinement=True,
                metagenome_id=metagenome_id,
            )
            session.add(refinement)
        session.commit()


def main():
    # init database and tables
    create_db_and_tables()
    table_names = get_table_names()
    print(f"db table names: {', '.join(table_names)}")

    # CRUD sample (this will take some time with the connection mapping...)
    # NOTE: Create two samples for testing...
    sponge_mg = create_sample_metagenome(
        name="lasonolide",
        metagenome_fpath="data/lasonolide/metagenome.filtered.fna",
        binning_fpath="data/lasonolide/binning.tsv",
        markers_fpath="data/lasonolide/bacteria.markers.tsv",
        # connections_fpath="data/lasonolide/cytoscape.connections.tab",
    )
    create_initial_refinements(sponge_mg.id)
    nubbins_mg = create_sample_metagenome(
        name="nubbins",
        metagenome_fpath="data/nubbins/scaffolds.fasta",
        binning_fpath="data/nubbins/nubbins.tsv",
        markers_fpath="data/nubbins/bacteria.markers.tsv",
    )
    create_initial_refinements(nubbins_mg.id)


if __name__ == "__main__":
    main()
