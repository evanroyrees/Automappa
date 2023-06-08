# -*- coding: utf-8 -*-

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.utils.figures import metric_boxplot
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_COVERAGE_BOXPLOT, "figure"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
    )
    def mag_summary_gc_content_boxplot_callback(
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
        fig = metric_boxplot(df=mag_df, metrics=["coverage"])
        return fig

    return html.Div(
        dcc.Loading(
            id=ids.LOADING_MAG_COVERAGE_BOXPLOT,
            children=[
                dcc.Graph(
                    id=ids.MAG_COVERAGE_BOXPLOT,
                    config={"displayModeBar": False, "displaylogo": False},
                )
            ],
            type="default",
            color="#0479a8",
        )
    )
