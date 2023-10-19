# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
from typing import Protocol, Optional, List, Tuple
from plotly import graph_objects as go

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class LengthOverviewBoxplotDataSource(Protocol):
    def get_length_boxplot_records(
        self, metagenome_id: int, cluster: Optional[str]
    ) -> List[Tuple[str, List[int]]]:
        ...


def render(app: DashProxy, source: LengthOverviewBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_LENGTH_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def mag_overview_length_boxplot_callback(metagenome_id: int) -> go.Figure:
        data = source.get_length_boxplot_records(metagenome_id)
        fig = metric_boxplot(data)
        return fig

    graph_config = dict(
        toImageButtonOptions=dict(
            format="svg",
            filename="mag-summary-length-boxplot",
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
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_OVERVIEW_LENGTH_BOXPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_OVERVIEW_LENGTH_BOXPLOT,
                        config=graph_config,
                    )
                ],
                type="default",
                color="#0479a8",
            )
        ]
    )
