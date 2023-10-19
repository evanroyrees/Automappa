# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go
from typing import Protocol, List, Tuple
from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class ClusterCoverageBoxplotDataSource(Protocol):
    def get_coverage_boxplot_records(
        self, metagenome_id: int, refinement_id: int
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: ClusterCoverageBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_COVERAGE_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
        prevent_initial_call=True,
    )
    def mag_summary_coverage_boxplot_callback(
        metagenome_id: int, refinement_id: int
    ) -> go.Figure:
        data = source.get_coverage_boxplot_records(
            metagenome_id, refinement_id=refinement_id
        )
        fig = metric_boxplot(data)
        return fig

    graph_config = dict(
        toImageButtonOptions=dict(
            format="svg",
            filename="mag-summary-MAG-coverage-boxplot",
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
        dcc.Loading(
            id=ids.LOADING_MAG_COVERAGE_BOXPLOT,
            children=[
                dcc.Graph(
                    id=ids.MAG_COVERAGE_BOXPLOT,
                    config=graph_config,
                )
            ],
            type="default",
            color="#0479a8",
        )
    )
