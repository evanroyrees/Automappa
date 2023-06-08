# -*- coding: utf-8 -*-

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.utils.figures import metric_boxplot
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_METRICS_BOXPLOT, "figure"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
    )
    def subset_by_selected_mag(sample: SampleTables, cluster_col: str) -> go.Figure:
        mag_summary_df = sample.binning.table
        if cluster_col not in mag_summary_df.columns:
            raise PreventUpdate
        mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
        mag_summary_df = mag_summary_df.loc[
            mag_summary_df[cluster_col].ne("unclustered")
        ]
        fig = metric_boxplot(df=mag_summary_df, metrics=["completeness", "purity"])
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
