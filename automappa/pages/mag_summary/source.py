#!/usr/bin/env python
import logging
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional, Tuple, Union

from sqlmodel import Session, and_, select, func
from automappa.data.database import engine
from automappa.data.models import Refinement, Contig, Marker
from automappa.data.schemas import ContigSchema

logger = logging.getLogger(__name__)

MARKER_SET_SIZE = 139


class SummaryDataSource(BaseModel):
    def compute_completeness_purity_metrics(
        self, metagenome_id: int, refinement_id: int
    ) -> Tuple[float, float]:
        marker_count_stmt = (
            select(func.count(Marker.id))
            .join(Contig)
            .where(
                Contig.metagenome_id == metagenome_id,
                Contig.refinements.any(
                    and_(
                        Refinement.outdated == False,
                        Refinement.id == refinement_id,
                    )
                ),
            )
        )
        unique_marker_stmt = (
            select(Marker.sacc)
            .join(Contig)
            .distinct()
            .where(
                Contig.metagenome_id == metagenome_id,
                Contig.refinements.any(
                    and_(
                        Refinement.outdated == False,
                        Refinement.id == refinement_id,
                    )
                ),
            )
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
        return completeness, purity

    def compute_length_sum_mbp(self, metagenome_id: int, refinement_id: int) -> float:
        contig_length_stmt = select(func.sum(Contig.length)).where(
            Contig.metagenome_id == metagenome_id,
            Contig.refinements.any(
                and_(
                    Refinement.outdated == False,
                    Refinement.id == refinement_id,
                )
            ),
        )
        with Session(engine) as session:
            length_sum = session.exec(contig_length_stmt).first() or 0
        length_sum_mbp = round(length_sum / 1_000_000, 3)
        return length_sum_mbp

    def get_completeness_purity_boxplot_records(
        self, metagenome_id: int
    ) -> List[Tuple[str, List[float]]]:
        completeness_metrics = []
        purities = []
        with Session(engine) as session:
            stmt = select(Refinement.id).where(
                Refinement.outdated == False, Refinement.metagenome_id == metagenome_id
            )
            refinement_ids = session.exec(stmt).all()
        for refinement_id in refinement_ids:
            (
                completeness,
                purity,
            ) = self.compute_completeness_purity_metrics(metagenome_id, refinement_id)
            completeness_metrics.append(completeness)
            purities.append(purity)
        return [
            (ContigSchema.COMPLETENESS.title(), completeness_metrics),
            (ContigSchema.PURITY.title(), purities),
        ]

    def get_gc_content_boxplot_records(
        self, metagenome_id: int, refinement_id: Optional[int] = 0
    ) -> List[Tuple[str, List[float]]]:
        stmt = select([Contig.gc_content]).where(Contig.metagenome_id == metagenome_id)
        if refinement_id:
            stmt = stmt.where(
                Contig.refinements.any(
                    and_(
                        Refinement.outdated == False,
                        Refinement.id == refinement_id,
                    )
                )
            )
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [("GC Content", results)]

    def get_length_boxplot_records(
        self, metagenome_id: int, refinement_id: Optional[int] = 0
    ) -> List[Tuple[str, List[int]]]:
        stmt = select([Contig.length]).where(Contig.metagenome_id == metagenome_id)
        if refinement_id:
            stmt = stmt.where(
                Contig.refinements.any(
                    and_(
                        Refinement.outdated == False,
                        Refinement.id == refinement_id,
                    )
                )
            )
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [(ContigSchema.LENGTH.title(), results)]

    def get_coverage_boxplot_records(
        self, metagenome_id: int, refinement_id: Optional[int] = 0
    ) -> List[Tuple[str, List[float]]]:
        stmt = select([Contig.coverage]).where(Contig.metagenome_id == metagenome_id)
        if refinement_id:
            stmt = stmt.where(
                Contig.refinements.any(
                    and_(
                        Refinement.outdated == False,
                        Refinement.id == refinement_id,
                    )
                )
            )
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [(ContigSchema.COVERAGE.title(), results)]

    def get_metrics_barplot_records(
        self, metagenome_id: int, refinement_id: int
    ) -> Tuple[str, List[float], List[float]]:
        completeness, purity = self.compute_completeness_purity_metrics(
            metagenome_id=metagenome_id, refinement_id=refinement_id
        )
        name = f"bin_{refinement_id} Metrics"
        x = [ContigSchema.COMPLETENESS.title(), ContigSchema.PURITY.title()]
        y = [completeness, purity]
        return name, x, y

    def get_mag_stats_summary_row_data(
        self, metagenome_id: int
    ) -> List[
        Dict[
            Literal[
                "refinement_id",
                "refinement_label",
                "length_sum_mbp",
                "completeness",
                "purity",
                "contig_count",
            ],
            Union[str, int, float],
        ]
    ]:
        stmt = select(Refinement).where(
            Refinement.metagenome_id == metagenome_id,
            Refinement.outdated == False,
        )
        row_data = {}
        with Session(engine) as session:
            refinements = session.exec(stmt).all()
            for refinement in refinements:
                contig_count = len(refinement.contigs)
                row_data[refinement.id] = {
                    "refinement_id": refinement.id,
                    "refinement_label": f"bin_{refinement.id}",
                    "contig_count": contig_count,
                }
            for refinement_id in row_data:
                completeness, purity = self.compute_completeness_purity_metrics(
                    metagenome_id, refinement_id
                )
                length_sum_mbp = self.compute_length_sum_mbp(
                    metagenome_id, refinement_id
                )
                row_data[refinement_id].update(
                    {
                        "completeness": completeness,
                        "purity": purity,
                        "length_sum_mbp": length_sum_mbp,
                    }
                )
        return list(row_data.values())

    def get_refinement_selection_dropdown_options(
        self, metagenome_id: int
    ) -> List[Dict[Literal["label", "value"], str]]:
        stmt = (
            select([Refinement.id])
            .where(
                Refinement.metagenome_id == metagenome_id,
                Refinement.outdated == False,
            )
            .distinct()
        )
        with Session(engine) as session:
            results = session.exec(stmt).all()
        return [dict(label=f"bin_{result}", value=result) for result in results]

    def get_taxonomy_sankey_records(
        self, metagenome_id: int, refinement_id: int
    ) -> pd.DataFrame:
        statement = select(
            Contig.header,
            Contig.superkingdom,
            Contig.phylum,
            Contig.klass,
            Contig.order,
            Contig.family,
            Contig.genus,
            Contig.species,
        ).where(
            Contig.metagenome_id == metagenome_id,
            Contig.refinements.any(Refinement.id == refinement_id),
        )
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
