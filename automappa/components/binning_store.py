#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import (
    DashProxy,
    Input,
    Serverside,
    Output,
    dcc,
)
from dash.exceptions import PreventUpdate

from automappa.data.source import SampleTables
from automappa.components import ids


def render(app: DashProxy) -> dcc.Store:
    @app.callback(
        Output(ids.BINNING_STORE, "data"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        memoize=True,
    )
    def query_binning_in_db(sample: SampleTables):
        if sample is None:
            raise PreventUpdate
        return Serverside(sample.binning.table)

    return dcc.Loading(dcc.Store(ids.BINNING_STORE), type="dot")
