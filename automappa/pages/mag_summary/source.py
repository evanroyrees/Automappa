#!/usr/bin/env python
import logging
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional, Tuple, Union

from sqlmodel import Session, select, func
from automappa.data.database import engine
from automappa.data.loader import Metagenome, Contig, Marker
from automappa.data.schemas import ContigSchema

logger = logging.getLogger(__name__)


class SummaryDataSource(BaseModel):
    def get_completeness_purity_boxplot_records(
        self, metagenome_id: int, cluster_col: str
    ) -> List[Tuple[str, pd.Series]]:
        # FIXME: Need to implement cluster column selection with Refinement BaseModel
        # if cluster_col not in mag_summary_df.columns:
        #     raise PreventUpdate
        # mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
        # mag_summary_df = mag_summary_df.loc[
        #     mag_summary_df[cluster_col].ne("unclustered")
        # ]
        completeness_stmt = (
            select(Contig.completeness)
            .where(
                Contig.metagenome_id == metagenome_id,
                Contig.cluster.isnot(None),
                Contig.cluster != "nan",
            )
            .group_by(Contig.cluster)
        )
        purity_stmt = select(Contig.purity).where(Contig.metagenome_id == metagenome_id)
        with Session(engine) as session:
            completeness_results = session.exec(completeness_stmt).all()
            purity_results = session.exec(purity_stmt).all()
        return [
            (ContigSchema.COMPLETENESS.title(), pd.Series(completeness_results)),
            (ContigSchema.PURITY.title(), pd.Series(purity_results)),
        ]
