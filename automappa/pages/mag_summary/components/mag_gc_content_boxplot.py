# -*- coding: utf-8 -*-

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.utils.figures import metric_boxplot
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_GC_CONTENT_BOXPLOT, "figure"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
    )
    def mag_summary_gc_content_boxplot_callback(
        sample: SampleTables, cluster_col: str, selected_mag: str
    ) -> go.Figure:
        bin_df = sample.binning.table
        refinement_df = sample.refinements.table.drop(columns="cluster")
        bin_df = bin_df.join(refinement_df, how="right")
        if cluster_col not in bin_df.columns:
            raise PreventUpdate
        bin_df = bin_df.dropna(subset=[cluster_col])
        mag_df = bin_df.loc[bin_df[cluster_col].eq(selected_mag)]
        mag_df = mag_df.round(2)
        fig = metric_boxplot(df=mag_df, metrics=["gc_content"])
        fig.update_traces(name="GC Content")
        return fig

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_GC_CONTENT_BOXPLOT,
                children=[
                    dcc.Graph(
                        id=ids.MAG_GC_CONTENT_BOXPLOT,
                        config={"displayModeBar": False, "displaylogo": False},
                    )
                ],
                type="default",
                color="#0479a8",
            )
        ]
    )
