#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.utils.figures import (
    taxonomy_sankey,
)

from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.TAXONOMY_DISTRIBUTION, "figure"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.SCATTERPLOT_2D, "selectedData"),
            Input(ids.TAXONOMY_DISTRIBUTION_DROPDOWN, "value"),
        ],
    )
    def taxonomy_distribution_figure_callback(
        sample: SampleTables,
        selected_contigs: Dict[str, List[Dict[str, str]]],
        selected_rank: str,
    ) -> go.Figure:
        df = sample.binning.table
        if selected_contigs and selected_contigs["points"]:
            contigs = {point["text"] for point in selected_contigs["points"]}
            df = df.loc[df.index.isin(contigs)]
        fig = taxonomy_sankey(df, selected_rank=selected_rank)
        return fig

    return html.Div(
        [
            html.Label("Figure 3: Taxonomic Distribution"),
            dcc.Loading(
                id=ids.LOADING_TAXONOMY_DISTRIBUTION,
                children=[
                    dcc.Graph(
                        id=ids.TAXONOMY_DISTRIBUTION,
                        config={
                            "displayModeBar": False,
                            "displaylogo": False,
                            "staticPlot": True,
                        },
                    )
                ],
                type="graph",
            ),
        ]
    )
