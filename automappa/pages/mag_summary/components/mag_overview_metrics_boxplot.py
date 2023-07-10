# -*- coding: utf-8 -*-

from typing import List, Protocol, Tuple
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class OverviewMetricsBoxplotDataSource(Protocol):
    def get_records(self, metagenome_id: int) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: OverviewMetricsBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_METRICS_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
    )
    def subset_by_selected_mag(metagenome_id: int, cluster_col: str) -> go.Figure:
        data = source.get_records(metagenome_id)
        fig = metric_boxplot(data=data)
        return fig

    return html.Div(
        dcc.Loading(
            id=ids.LOADING_MAG_OVERVIEW_METRICS_BOXPLOT,
            children=[
                dcc.Graph(
                    id=ids.MAG_OVERVIEW_METRICS_BOXPLOT,
                    config={"displayModeBar": False, "displaylogo": False},
                )
            ],
            type="default",
            color="#0479a8",
        )
    )
