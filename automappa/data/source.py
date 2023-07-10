from functools import partial
import itertools
import uuid
import logging
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional, Tuple, Union

from sqlmodel import SQLModel, Session, select, func
import numpy as np

from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from automappa.data import loader


from automappa.data.database import engine, create_db_and_tables
from automappa.data.loader import (
    get_table,
    in_table_names,
    read_cytoscape_connections,
    Metagenome,
    Contig,
    Marker,
    CytoscapeConnection,
    create_sample_metagenome,
    validate_uploader,
)
from automappa.data.schemas import ContigSchema

logger = logging.getLogger(__name__)


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


class AnnotationTable(BaseModel):
    id: str
    index_col: Optional[str] = "contig"

    @property
    def sample_checksum(self):
        return self.id.split("-")[0]

    @property
    def name(self):
        return "-".join(self.id.split("-")[1:])

    @property
    def table(self):
        return get_table(self.id, index_col=self.index_col)

    @property
    def exists(self):
        return in_table_names(self.id)

    @property
    def columns(self):
        return self.table.columns


class KmerTable(BaseModel):
    assembly: AnnotationTable
    size: Literal[3, 4, 5] = 5
    norm_method: Literal["am_clr", "ilr", "clr"] = "am_clr"
    embed_dims: Optional[int] = 2
    # embed_dims: conint(gt=1, lt=100) = 2
    embed_method: Literal["bhsne", "sksne", "umap", "densmap", "trimap"] = "bhsne"

    @property
    def counts(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.assembly.id.replace("-metagenome", f"-{self.size}mers")
        )

    @property
    def norm_freqs(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.assembly.id.replace(
                "-metagenome", f"-{self.size}mers-{self.norm_method}"
            )
        )

    @property
    def embedding(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.assembly.id.replace(
                "-metagenome",
                f"-{self.size}mers-{self.norm_method}-{self.embed_method}",
            )
        )


class Scatterplot2DSource(BaseModel):
    def coverage_filter(coverage_range: Tuple[float, float]) -> pd.DataFrame:
        return get_contigs_from_coverage_range((10, 20))


class CytoscapeConnectionsTable(BaseModel):
    id: str

    @property
    def sample_checksum(self):
        return self.id.split("-")[0]

    @property
    def name(self):
        return "-".join(self.id.split("-")[1:])

    @property
    def table(self):
        return read_cytoscape_connections()

    @property
    def exists(self):
        return in_table_names(self.id)

    @property
    def columns(self):
        return self.table.columns


class SampleTables(BaseModel):
    binning: Optional[AnnotationTable]
    markers: Optional[AnnotationTable]
    metagenome: Optional[AnnotationTable]
    cytoscape: Optional[CytoscapeConnectionsTable]
    # The following are created after user upload
    # via:
    # celery tasks (see tasks.py)
    refinements: Optional[AnnotationTable]
    # geom_medians: Optional[str]

    @property
    def kmers(self) -> List[KmerTable]:
        settings = []
        sizes = [3, 4, 5]
        norm_methods = ["am_clr", "ilr"]
        embed_methods = ["bhsne", "densmap", "umap", "sksne", "trimap"]
        for size, norm_method, embed_method in itertools.product(
            sizes, norm_methods, embed_methods
        ):
            settings.append(
                KmerTable(
                    assembly=self.metagenome,
                    size=size,
                    norm_method=norm_method,
                    embed_dims=2,
                    embed_method=embed_method,
                )
            )
        return settings

    @property
    def embeddings(self) -> List[AnnotationTable]:
        kmer_sizes = set([kmer_table.size for kmer_table in self.kmers])
        norm_methods = set([kmer_table.norm_method for kmer_table in self.kmers])
        # NOTE: The corresponding table-name suffix format (AnnotationTable(id=...))
        # is at https://github.com/WiscEvan/Automappa/blob/977dbbf6dca8cc62f974eb1c6a2f48fc25f2ddb2/automappa/tasks.py#L149
        return [
            AnnotationTable(
                id=self.metagenome.id.replace(
                    "-metagenome", f"-{kmer_size}mers-{norm_method}-embeddings"
                ),
                index_col="contig",
            )
            for kmer_size, norm_method in itertools.product(kmer_sizes, norm_methods)
        ]

    @property
    def marker_symbols(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.markers.id.replace("-markers", "-marker-symbols")
        )

    class Config:
        arbitrary_types_allowed = True
        smart_union = True


## DataSource filter methods


def get_mag_completeness_purities(metagenome_id: int) -> List[Tuple[float, float]]:
    with Session(engine) as session:
        results = session.exec(
            select(Contig)
            .where(Contig.metagenome_id == metagenome_id)
            .where(Contig.cluster.isnot(None), Contig.cluster != "nan")
            .group_by(Contig.cluster)
        ).all()
    return [(result.cluster, result.completeness, result.purity) for result in results]


def get_gc_contents(metagenome_id: int) -> List[float]:
    with Session(engine) as session:
        results = session.exec(
            select(Contig).join(Metagenome).where(Metagenome.id == metagenome_id)
        ).all()
    return [result.gc_content for result in results]


def get_lengths(metagenome_id: int) -> List[float]:
    with Session(engine) as session:
        results = session.exec(
            select(Contig).where(Contig.metagenome_id == metagenome_id)
        ).all()
    return [result.length for result in results]


def get_coverages(metagenome_id: int) -> List[float]:
    with Session(engine) as session:
        statement = select(Contig).where(Contig.metagenome_id == metagenome_id)
        results = session.exec(statement).all()
    return [result.coverage for result in results]


def get_contigs_from_coverage_range(
    metagenome_id: int, coverage_range: Tuple[float, float]
) -> List[Contig]:
    min_coverage, max_coverage = coverage_range
    with Session(engine) as session:
        statement = (
            select(Contig)
            .where(
                Contig.coverage >= min_coverage,
                Contig.coverage <= max_coverage,
            )
            .join(Metagenome)
            .where(Metagenome.id == metagenome_id)
        )
        results = session.exec(statement).all()
    return sqlmodel_to_df(results)


def get_coverage_quantiles(
    quantiles: List[int] = [0, 0.25, 0.5, 0.75, 1]
) -> List[float]:
    with Session(engine) as session:
        statement = select(Contig.coverage)
        coverages = session.exec(statement).all()
    quantile = np.quantile(coverages, q=quantiles)
    return quantile


def get_min_max_coverages() -> Tuple[float, float]:
    with Session(engine) as session:
        statement = select(func.min(Contig.coverage), func.max(Contig.coverage))
        min_cov, max_cov = session.exec(statement).first()
    return min_cov, max_cov


def get_scatterplot_2d_data(
    metagenome_id: int, coverage_range: Tuple[float, float]
) -> pd.DataFrame:
    # refinements_filter
    # coverage_range_filter
    min_coverage, max_coverage = coverage_range
    with Session(engine) as session:
        statement = (
            select(Contig)
            .where(Contig.metagenome_id == metagenome_id)
            .where(
                Contig.coverage >= min_coverage,
                Contig.coverage <= max_coverage,
            )
        )
        results = session.exec(statement).all()
    # join_markers
    return sqlmodel_to_df(results)


def main():
    # init database and tables
    create_db_and_tables()
    source = HomeDataSource()
    markers = source.create_markers()
    # metagenome_getter(contigs_getter(markers_getter()))
    contigs = source.create_contigs(markers)
    source.create_metagenome(contigs)
    sample_names = source.get_sample_names()
    print(f"{sample_names=}")
    for sample_name in sample_names:
        name_is_unique = source.name_is_unique(sample_name)
        print(f"{sample_name=}, {name_is_unique=}")
        marker_count = source.marker_count(sample_name)
        print(f"{sample_name=}, {marker_count=}")
        contig_count = source.contig_count(sample_name)
        print(f"{sample_name=}, {contig_count=}")
        connections_count = source.connections_count(sample_name)
        print(f"{sample_name=}, {connections_count=}")
        mags = get_mag_completeness_purities(sample_name)
        print(mags)
    # min_cov, max_cov = get_min_max_coverages()
    # print(f"min: {min_cov:,}, max: {max_cov:,}")
    # quantiles = get_coverage_quantiles()
    # print(f"coverage quantiles: {quantiles}")
    # res = get_mag_completeness_purities()
    # print(res)
    # contig_df = get_contigs_from_coverage_range((10, 20))


if __name__ == "__main__":
    main()
