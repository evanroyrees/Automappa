# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go
from typing import Protocol, List, Tuple

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class GcContentBoxplotDataSource(Protocol):
    def get_gc_content_boxplot_records(
        self, metagenome_id: int, refinement_id: int
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: GcContentBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_GC_CONTENT_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
        prevent_initial_call=True,
    )
    def mag_summary_gc_content_boxplot_callback(
        metagenome_id: int, refinement_id: int
    ) -> go.Figure:
        data = source.get_gc_content_boxplot_records(
            metagenome_id, refinement_id=refinement_id
        )
        fig = metric_boxplot(data)
        return fig

    graph_config = dict(
        toImageButtonOptions=dict(
            format="svg",
            filename="mag-summary-MAG-gc-content-boxplot",
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
            dcc.Loading(
                dcc.Graph(
                    id=ids.MAG_GC_CONTENT_BOXPLOT,
                    config=graph_config,
                ),
                id=ids.LOADING_MAG_GC_CONTENT_BOXPLOT,
                type="default",
                color="#0479a8",
            )
        ]
    )
