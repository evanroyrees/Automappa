# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go
from typing import Protocol, List, Tuple, Optional

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class GcContentBoxplotDataSource(Protocol):
    def get_gc_content_boxplot_records(
        self, metagenome_id: int, cluster: Optional[str]
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: GcContentBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_GC_CONTENT_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
    )
    def mag_summary_gc_content_boxplot_callback(
        metagenome_id: int, cluster: str
    ) -> go.Figure:
        data = source.get_gc_content_boxplot_records(metagenome_id, cluster=cluster)
        fig = metric_boxplot(data)
        return fig

    return html.Div(
        [
            dcc.Loading(
                dcc.Graph(
                    id=ids.MAG_GC_CONTENT_BOXPLOT,
                    config={"displayModeBar": False, "displaylogo": False},
                ),
                id=ids.LOADING_MAG_GC_CONTENT_BOXPLOT,
                type="default",
                color="#0479a8",
            )
        ]
    )
