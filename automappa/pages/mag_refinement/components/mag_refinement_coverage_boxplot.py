#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Protocol, Tuple
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
from plotly import graph_objects as go

from automappa.utils.figures import metric_boxplot

from automappa.components import ids


class RefinementCoverageBoxplotDataSource(Protocol):
    def get_coverage_boxplot_records(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: RefinementCoverageBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_REFINEMENT_COVERAGE_BOXPLOT, "figure"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
        ],
    )
    def subset_coverage_boxplot_by_scatterplot_selection(
        metagenome_id: int,
        selected_data: Dict[str, List[Dict[str, str]]],
    ) -> go.Figure:
        headers = (
            {point["text"] for point in selected_data["points"]}
            if selected_data
            else None
        )
        data = source.get_coverage_boxplot_records(metagenome_id, headers=headers)
        fig = metric_boxplot(data, boxmean="sd")
        return fig

    graph_config = dict(
        toImageButtonOptions=dict(
            format="svg",
            filename="mag-refinement-coverage-boxplot",
        ),
        displayModeBar="hover",
        displaylogo=False,
        modeBarButtonsToAdd=["toImage"],
        modeBarButtonsToRemove=[
            "pan2d",
            "select2d",
            "lasso2d",
            "resetScale2d",
            "zoomOut2d",
        ],
    )

    return html.Div(
        [
            html.Label("Figure 4: MAG Refinement Coverage Boxplot"),
            dcc.Loading(
                id=ids.LOADING_MAG_REFINEMENT_COVERAGE_BOXPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_REFINEMENT_COVERAGE_BOXPLOT,
                        config=graph_config,
                    )
                ],
                type="dot",
                color="#646569",
            ),
        ]
    )
