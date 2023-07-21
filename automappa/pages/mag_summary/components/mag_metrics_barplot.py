# -*- coding: utf-8 -*-
from typing import Protocol, List, Tuple

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.utils.figures import metric_barplot
from automappa.components import ids


class ClusterMetricsBarplotDataSource(Protocol):
    def get_metrics_barplot_records(
        self, metagenome_id: int, refinement_id: int
    ) -> Tuple[str, List[float], List[float]]:
        ...


def render(app: DashProxy, source: ClusterMetricsBarplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_METRICS_BARPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
        prevent_initial_call=True,
    )
    def mag_metrics_callback(metagenome_id: int, refinement_id: int) -> go.Figure:
        data = source.get_metrics_barplot_records(
            metagenome_id, refinement_id=refinement_id
        )
        fig = metric_barplot(data)
        return fig

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_METRICS_BARPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_METRICS_BARPLOT,
                        config={"displayModeBar": False, "displaylogo": False},
                    )
                ],
                type="dot",
                color="#646569",
            )
        ]
    )
