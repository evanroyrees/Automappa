# -*- coding: utf-8 -*-

from typing import List, Protocol, Tuple
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class OverviewMetricsBoxplotDataSource(Protocol):
    def get_completeness_purity_boxplot_records(
        self, metagenome_id: int
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: OverviewMetricsBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_METRICS_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def subset_by_selected_mag(metagenome_id: int) -> go.Figure:
        data = source.get_completeness_purity_boxplot_records(metagenome_id)
        fig = metric_boxplot(data=data)
        return fig

    return html.Div(
        dcc.Loading(
            dcc.Graph(
                id=ids.MAG_OVERVIEW_METRICS_BOXPLOT,
                config={"displayModeBar": False, "displaylogo": False},
            ),
            id=ids.LOADING_MAG_OVERVIEW_METRICS_BOXPLOT,
            type="default",
            color="#0479a8",
        )
    )
