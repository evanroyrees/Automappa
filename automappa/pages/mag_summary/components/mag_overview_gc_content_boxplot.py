# -*- coding: utf-8 -*-

from typing import List, Optional, Protocol, Tuple
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class GcContentBoxplotDataSource(Protocol):
    def get_gc_content_boxplot_records(
        self, metagenome_id: int, cluster: Optional[str]
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: GcContentBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_GC_CONTENT_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def mag_overview_gc_content_boxplot_callback(metagenome_id: int) -> go.Figure:
        data = source.get_gc_content_boxplot_records(metagenome_id=metagenome_id)
        fig = metric_boxplot(data=data)
        return fig

    graph_config = dict(
        toImageButtonOptions=dict(
            format="svg",
            filename="mag-summary-gc-content-boxplot",
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
                id=ids.LOADING_MAG_OVERVIEW_GC_CONTENT_BOXPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_OVERVIEW_GC_CONTENT_BOXPLOT,
                        config=graph_config,
                    )
                ],
                type="dot",
                color="#646569",
            )
        ]
    )
