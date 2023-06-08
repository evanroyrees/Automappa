# -*- coding: utf-8 -*-

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.utils.figures import metric_barplot
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_METRICS_BARPLOT, "figure"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
    )
    def mag_metrics_callback(
        sample: SampleTables, cluster_col: str, selected_mag: str
    ) -> go.Figure:
        if not selected_mag:
            raise PreventUpdate
        bin_df = sample.binning.table
        refinement_df = sample.refinements.table.drop(columns="cluster")
        mag_summary_df = bin_df.join(refinement_df, how="right")
        if cluster_col not in mag_summary_df.columns:
            raise PreventUpdate
        mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
        mag_df = mag_summary_df.loc[mag_summary_df[cluster_col].eq(selected_mag)]
        mag_df = mag_df.round(2)
        fig = metric_barplot(
            df=mag_df, metrics=["completeness", "purity"], name=selected_mag
        )
        return fig

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_METRICS_BARPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_METRICS_BARPLOT,
                        config={"displayModeBar": False, "displaylogo": False},
                    )
                ],
                type="dot",
                color="#646569",
            )
        ]
    )
