# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from typing import Protocol, List, Tuple
from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class ClusterLengthBoxplotDataSource(Protocol):
    def get_length_boxplot_records(
        self, metagenome_id: int, refinement_id: int
    ) -> List[Tuple[str, List[int]]]:
        ...


def render(app: DashProxy, source: ClusterLengthBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_LENGTH_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
        prevent_initial_call=True,
    )
    def mag_summary_gc_content_boxplot_callback(
        metagenome_id: int, refinement_id: int
    ) -> go.Figure:
        data = source.get_length_boxplot_records(
            metagenome_id, refinement_id=refinement_id
        )
        fig = metric_boxplot(data)
        return fig

    graph_config = dict(
        toImageButtonOptions=dict(
            format="svg",
            filename="mag-summary-MAG-length-boxplot",
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
                id=ids.LOADING_MAG_LENGTH_BOXPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_LENGTH_BOXPLOT,
                        config=graph_config,
                    )
                ],
                type="dot",
                color="#646569",
            )
        ]
    )
