#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

import dash_bootstrap_components as dbc

from automappa.data.source import SampleTables
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.REFINEMENTS_DOWNLOAD, "data"),
        [
            Input(ids.REFINEMENTS_DOWNLOAD_BUTTON, "n_clicks"),
            Input(ids.SELECTED_TABLES_STORE, "data"),
        ],
    )
    def download_refinements(
        n_clicks: int,
        sample: SampleTables,
    ) -> Dict[str, "str | bool"]:
        if not n_clicks:
            raise PreventUpdate
        return dcc.send_data_frame(
            sample.refinements.table.to_csv, "refinements.csv", index=False
        )

    # Download Refinements Button
    return html.Div(
        [
            dbc.Button(
                "Download Refinements",
                id=ids.REFINEMENTS_DOWNLOAD_BUTTON,
                n_clicks=0,
                color="primary",
            ),
            dcc.Download(id=ids.REFINEMENTS_DOWNLOAD),
        ]
    )
