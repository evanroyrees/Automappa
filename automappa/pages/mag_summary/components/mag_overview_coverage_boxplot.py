# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from typing import Protocol, List, Tuple, Optional
from plotly import graph_objects as go

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class OverviewCoverageBoxplotDataSource(Protocol):
    def get_coverage_boxplot_records(
        self, metagenome_id: int, cluster: Optional[str]
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: OverviewCoverageBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_COVERAGE_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def mag_overview_coverage_boxplot_callback(metagenome_id: int) -> go.Figure:
        data = source.get_coverage_boxplot_records(metagenome_id)
        fig = metric_boxplot(data)
        return fig

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_COVERAGE_BOXPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_OVERVIEW_COVERAGE_BOXPLOT,
                        config={"displayModeBar": False, "displaylogo": False},
                    )
                ],
                type="dot",
                color="#646569",
            )
        ]
    )
