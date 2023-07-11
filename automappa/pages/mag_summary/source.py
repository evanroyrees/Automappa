#!/usr/bin/env python
import logging
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional, Tuple, Union

from sqlmodel import Session, select, func
from automappa.data.database import engine
from automappa.data.loader import Contig, Marker
from automappa.data.schemas import ContigSchema

logger = logging.getLogger(__name__)


class SummaryDataSource(BaseModel):
    def get_completeness_purity_boxplot_records(
        self, metagenome_id: int
    ) -> List[Tuple[str, List[float]]]:
        MARKER_SET_SIZE = 139
        marker_count_stmt = (
            select([func.count(Marker.id)])
            .join(Contig)
            .where(Contig.metagenome_id == metagenome_id)
            .group_by(Contig.cluster)
        )
        unique_marker_stmt = (
            select(Marker.sacc)
            .join(Contig)
            .distinct()
            .where(Contig.metagenome_id == metagenome_id)
            .group_by(Contig.cluster)
        )
        with Session(engine) as session:
            markers_count = session.exec(marker_count_stmt).all()
            unique_marker_count = session.exec(
                select([func.count()]).select_from(unique_marker_stmt)
            ).all()

        completeness = round(unique_marker_count / MARKER_SET_SIZE * 100, 2)
        purity = (
            round(unique_marker_count / markers_count * 100, 2) if markers_count else 0
        )
        return [
            (ContigSchema.COMPLETENESS.title(), [completeness]),
            (ContigSchema.PURITY.title(), [purity]),
        ]

    def get_gc_content_boxplot_records(
        self, metagenome_id: int, cluster: Optional[str] = ""
    ) -> List[Tuple[str, List[float]]]:
        stmt = select([Contig.gc_content]).where(Contig.metagenome_id == metagenome_id)
        if cluster:
            stmt = stmt.where(Contig.cluster == cluster)
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [("GC Content", results)]

    def get_length_boxplot_records(
        self, metagenome_id: int, cluster: Optional[str] = ""
    ) -> List[Tuple[str, List[int]]]:
        stmt = select([Contig.length]).where(Contig.metagenome_id == metagenome_id)
        if cluster:
            stmt = stmt.where(Contig.cluster == cluster)
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [(ContigSchema.LENGTH.title(), results)]

    def get_coverage_boxplot_records(
        self, metagenome_id: int, cluster: Optional[str] = ""
    ) -> List[Tuple[str, List[float]]]:
        stmt = select([Contig.coverage]).where(Contig.metagenome_id == metagenome_id)
        if cluster:
            stmt = stmt.where(Contig.cluster == cluster)
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [(ContigSchema.COVERAGE.title(), results)]

    def get_metrics_barplot_records(
        self, metagenome_id: int, cluster: Optional[str]
    ) -> Tuple[str, List[float], List[float]]:
        MARKER_SET_SIZE = 139
        marker_count_stmt = (
            select(func.count(Marker.id))
            .join(Contig)
            .where(Contig.metagenome_id == metagenome_id)
            .where(Contig.cluster == cluster)
        )
        unique_marker_stmt = (
            select(Marker.sacc)
            .join(Contig)
            .distinct()
            .where(Contig.metagenome_id == metagenome_id)
            .where(Contig.cluster == cluster)
        )
        with Session(engine) as session:
            markers_count = session.exec(marker_count_stmt).first() or 0
            unique_marker_count = session.exec(
                select(func.count()).select_from(unique_marker_stmt)
            ).first()

        completeness = round(unique_marker_count / MARKER_SET_SIZE * 100, 2)
        purity = (
            round(unique_marker_count / markers_count * 100, 2) if markers_count else 0
        )

        name = f"{cluster} Metrics"
        x = [ContigSchema.COMPLETENESS.title(), ContigSchema.PURITY.title()]
        y = [completeness, purity]
        return name, x, y

    def get_cluster_selection_dropdown_options(
        self, metagenome_id: int
    ) -> List[Dict[Literal["label", "value"], str]]:
        stmt = (
            select([Contig.cluster])
            .where(
                Contig.metagenome_id == metagenome_id,
                Contig.cluster.isnot(None),
                Contig.cluster != "nan",
            )
            .distinct()
        )
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [dict(label=result, value=result) for result in results]

    def get_taxonomy_sankey_records(
        self, metagenome_id: int, cluster: str
    ) -> pd.DataFrame:
        statement = select(
            [
                Contig.header,
                Contig.superkingdom,
                Contig.phylum,
                Contig.klass,
                Contig.order,
                Contig.family,
                Contig.genus,
                Contig.species,
            ]
        ).where(Contig.metagenome_id == metagenome_id, Contig.cluster == cluster)
        with Session(engine) as session:
            results = session.exec(statement).all()

        columns = [
            ContigSchema.HEADER,
            ContigSchema.DOMAIN,
            ContigSchema.PHYLUM,
            ContigSchema.CLASS,
            ContigSchema.ORDER,
            ContigSchema.FAMILY,
            ContigSchema.GENUS,
            ContigSchema.SPECIES,
        ]

        df = pd.DataFrame.from_records(
            results,
            index=ContigSchema.HEADER,
            columns=columns,
        ).fillna("unclassified")

        for rank in df.columns:
            df[rank] = df[rank].map(lambda taxon: f"{rank[0]}_{taxon}")

        return df
