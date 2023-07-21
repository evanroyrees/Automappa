#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Protocol
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
import pandas as pd
from plotly import graph_objects as go

# from automappa.data.source import SampleTables
from automappa.utils.figures import (
    taxonomy_sankey,
)

from automappa.components import ids


class TaxonomyDistributionDataSource(Protocol):
    def get_sankey_records(
        self,
        metagenome_id: int,
        headers: Optional[List[str]],
        selected_rank: Optional[str],
    ) -> pd.DataFrame:
        ...


def render(app: DashProxy, source: TaxonomyDistributionDataSource) -> html.Div:
    @app.callback(
        Output(ids.TAXONOMY_DISTRIBUTION, "figure"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
            Input(ids.TAXONOMY_DISTRIBUTION_DROPDOWN, "value"),
        ],
    )
    def taxonomy_distribution_figure_callback(
        metagenome_id: int,
        selected_contigs: Dict[str, List[Dict[str, str]]],
        selected_rank: str,
    ) -> go.Figure:
        if selected_contigs and selected_contigs["points"]:
            headers = {point["text"] for point in selected_contigs["points"]}
        else:
            headers = None
        df = source.get_sankey_records(
            metagenome_id, headers=headers, selected_rank=selected_rank
        )
        fig = taxonomy_sankey(df)
        return fig

    return html.Div(
        [
            html.Label("Figure 3: Taxonomic Distribution"),
            dcc.Loading(
                dcc.Graph(
                    id=ids.TAXONOMY_DISTRIBUTION,
                    config={
                        "displayModeBar": False,
                        "displaylogo": False,
                        "staticPlot": False,
                    },
                ),
                id=ids.LOADING_TAXONOMY_DISTRIBUTION,
                type="graph",
            ),
        ]
    )
