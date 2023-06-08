# -*- coding: utf-8 -*-

from typing import Dict, List
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.data.source import SampleTables
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_SELECTION_DROPDOWN, "options"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.MAG_SUMMARY_CLUSTER_COL_DROPDOWN, "value"),
    )
    def mag_selection_dropdown_options_callback(
        sample: SampleTables, cluster_col: str
    ) -> List[Dict[str, str]]:
        df = sample.refinements.table
        if cluster_col not in df.columns:
            options = []
        else:
            options = [
                {"label": cluster, "value": cluster}
                for cluster in df[cluster_col].dropna().unique()
            ]
        return options

    return html.Div(
        [
            html.Label("MAG Selection Dropdown"),
            dcc.Dropdown(
                id=ids.MAG_SELECTION_DROPDOWN,
                clearable=True,
                placeholder="Select a MAG from this dropdown for a MAG-specific summary",
            ),
        ]
    )
