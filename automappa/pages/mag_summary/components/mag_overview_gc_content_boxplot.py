# -*- coding: utf-8 -*-

from typing import List, Protocol, Tuple
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.utils.figures import metric_boxplot
from automappa.components import ids


class GcContentBoxplotDataSource(Protocol):
    def get_gc_content_records(
        self, metagenome_id: int, cluster_col: str
    ) -> List[Tuple[str, List[float]]]:
        ...


def render(app: DashProxy, source: GcContentBoxplotDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_GC_CONTENT_BOXPLOT, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
    )
    def mag_overview_gc_content_boxplot_callback(
        metagenome_id: int, cluster_col: str
    ) -> go.Figure:
        # FIXME: Come back and compute metric...
        data = source.get_gc_content_records(
            metagenome_id=metagenome_id, cluster_col=cluster_col
        )
        if cluster_col not in mag_summary_df.columns:
            raise PreventUpdate
        mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
        mag_summary_df = mag_summary_df.loc[
            mag_summary_df[cluster_col].ne("unclustered")
        ]
        fig = metric_boxplot(data=data)
        return fig

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_OVERVIEW_GC_CONTENT_BOXPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_OVERVIEW_GC_CONTENT_BOXPLOT,
                        config={"displayModeBar": False, "displaylogo": False},
                    )
                ],
                type="dot",
                color="#646569",
            )
        ]
    )
