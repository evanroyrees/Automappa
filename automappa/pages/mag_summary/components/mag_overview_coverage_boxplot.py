# -*- coding: utf-8 -*-

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.utils.figures import metric_boxplot
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_OVERVIEW_COVERAGE_BOXPLOT, "figure"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
    )
    def mag_overview_coverage_boxplot_callback(
        sample: SampleTables, cluster_col: str
    ) -> go.Figure:
        mag_summary_df = sample.binning.table
        if cluster_col not in mag_summary_df.columns:
            raise PreventUpdate
        mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
        mag_summary_df = mag_summary_df.loc[
            mag_summary_df[cluster_col].ne("unclustered")
        ]
        fig = metric_boxplot(mag_summary_df, metrics=["coverage"])
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
