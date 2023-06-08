# -*- coding: utf-8 -*-

from typing import Dict, List
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.data.source import SampleTables
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "options"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
    )
    def mag_summary_cluster_col_dropdown_options_callback(
        sample: SampleTables,
    ) -> List[Dict[str, str]]:
        refinement_df = sample.refinements.table
        return [
            {"label": col.title(), "value": col}
            for col in refinement_df.columns
            if "cluster" in col or "refinement" in col
        ]

    return html.Div(
        [
            html.Label("MAG Summary Cluster Column Dropdown"),
            dcc.Dropdown(
                id=ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN,
                placeholder="Select a cluster column to compute MAG summary metrics",
                clearable=False,
            ),
        ]
    )
