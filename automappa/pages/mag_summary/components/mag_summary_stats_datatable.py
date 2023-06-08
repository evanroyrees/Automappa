# -*- coding: utf-8 -*-

from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.data.source import SampleTables
from automappa.tasks import get_metabin_stats_summary
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_SUMMARY_STATS_DATATABLE, "children"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
    )
    def mag_summary_stats_datatable_callback(
        sample: SampleTables, cluster_col: str
    ) -> DataTable:
        if cluster_col is None:
            raise PreventUpdate
        stats_df = get_metabin_stats_summary(
            binning_table=sample.binning.id,
            refinements_table=sample.refinements.id,
            markers_table=sample.markers.id,
            cluster_col=cluster_col,
        )
        return DataTable(
            data=stats_df.to_dict("records"),
            columns=[
                {"name": col.replace("_", " "), "id": col} for col in stats_df.columns
            ],
            style_table={"overflowX": "auto"},
            style_cell={
                "height": "auto",
                # all three widths are needed
                "width": "120px",
                "minWidth": "120px",
                "maxWidth": "120px",
                "whiteSpace": "normal",
            },
            fixed_rows={"headers": True},
        )

    return html.Div(
        children=[
            html.Label("Table 1. MAGs Summary"),
            dcc.Loading(
                id=ids.LOADING_MAG_SUMMARY_STATS_DATATABLE,
                children=[html.Div(id=ids.MAG_SUMMARY_STATS_DATATABLE)],
                type="circle",
                color="#646569",
            ),
        ]
    )
