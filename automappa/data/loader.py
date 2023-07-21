#!/usr/bin/env python
# DataLoader for Autometa results ingestion
import logging
from pathlib import Path
import uuid
import pandas as pd

from functools import partial, reduce
from typing import Callable, List, Optional, Union

from Bio import SeqIO
from sqlmodel import Session, select, SQLModel

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


def sqlmodel_to_df(objects: List[SQLModel], set_index: bool = True) -> pd.DataFrame:
    """Converts SQLModel objects into a Pandas DataFrame.

    From https://github.com/tiangolo/sqlmodel/issues/215#issuecomment-1092348993

    Usage
    ----------
    df = sqlmodel_to_df(list_of_sqlmodels)
    Parameters
    ----------
    :param objects: List[SQLModel]: List of SQLModel objects to be converted.
    :param set_index: bool: Sets the first column, usually the primary key, to dataframe index.
    """

    records = [obj.dict() for obj in objects]
    columns = list(objects[0].schema()["properties"].keys())
    df = pd.DataFrame.from_records(records, columns=columns)
    return df.set_index(columns[0]) if set_index else df


def validate_uploader(
    is_completed: bool, filenames: List[str], upload_id: uuid.UUID
) -> Union[Path, None]:
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
        pass
        # Need to ensure Seq column is in contigs otherwise add them
        # contig_seq_df = pd.DataFrame(
        #     [
        #         dict(header=record.id, seq=str(record.seq))
        #         for record in SeqIO.parse(metagenome_fpath, "fasta")
        #     ]
        # )
        # merge_seq_column = partial(add_seq_column, seqrecord_df=contig_seq_df)
    metagenome = Metagenome(name=name, contigs=contigs)
    with Session(engine) as session:
        session.add(metagenome)
        session.commit()
        session.refresh(metagenome)
    return metagenome


def read_metagenome(metagenome_id: int) -> Metagenome:
    with Session(engine) as session:
        metagenomes = session.exec(
            select(Metagenome).where(Metagenome.id == metagenome_id)
        ).first()
    return metagenomes


def read_metagenomes() -> List[Metagenome]:
    with Session(engine) as session:
        metagenomes = session.exec(select(Metagenome)).all()
    return metagenomes


def update_metagenomes() -> None:
    raise NotImplemented


def delete_metagenomes() -> None:
    raise NotImplemented


def rename_class_column_to_klass(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={ContigSchema.CLASS: ContigSchema.KLASS})


def rename_contig_column_to_header(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={ContigSchema.CONTIG: ContigSchema.HEADER})


def replace_cluster_na_values_with_unclustered(df: pd.DataFrame) -> pd.DataFrame:
    return df.fillna(value={ContigSchema.CLUSTER: "unclustered"})


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
            replace_cluster_na_values_with_unclustered,
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
    markers = [Marker(**row) for row in data.to_dict("records")]
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
    cytoscape_connections = [
        CytoscapeConnection(**record) for record in cyto_df.to_dict("records")
    ]
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
        replace_cluster_na_values_with_unclustered,
        merge_seq_column,
        merge_markers_column,
    )
    raw_binning = load_contigs(binning_fpath)
    contig_df = contig_preprocessor(raw_binning)
    nonmarker_contigs_mask = contig_df.markers.isna()
    nonmarker_contigs = [
        Contig(**record)
        for record in contig_df.loc[nonmarker_contigs_mask]
        .drop(columns=["markers"])
        .to_dict("records")
    ]
    marker_contigs = [
        Contig(**record)
        for record in contig_df.loc[~nonmarker_contigs_mask].to_dict("records")
    ]
    contigs = nonmarker_contigs + marker_contigs
    # Add cytoscape connection mapping if available
    if connections_fpath:
        connections_df = load_cytoscape_connections(connections_fpath)
        connections = [
            CytoscapeConnection(**record)
            for record in connections_df.to_dict("records")
        ]
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
            Contig.cluster != "unclustered",
        )
        .distinct()
    )
    with Session(engine) as session:
        clusters = session.exec(clusters_stmt).all()

        for cluster in clusters:
            contigs_stmt = select(Contig).where(Contig.cluster == cluster)
            contigs = session.exec(contigs_stmt).all()

            refinement = Refinement(
                contigs=contigs,
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
