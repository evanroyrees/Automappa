#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash.dash_table import DataTable

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.data.source import SampleTables

from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.REFINEMENTS_TABLE, "children"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        ],
    )
    def refinements_table_callback(
        sample: SampleTables,
        btn_clicks: int,
    ) -> DataTable:
        return DataTable(
            data=sample.refinements.table.to_dict("records"),
            columns=[
                {"name": col, "id": col} for col in sample.refinements.table.columns
            ],
            style_cell={"textAlign": "center"},
            style_cell_conditional=[
                {"if": {"column_id": "contig"}, "textAlign": "right"}
            ],
            virtualization=True,
        )

    return html.Div(
        dcc.Loading(
            id=ids.LOADING_REFINEMENTS_TABLE,
            children=[html.Div(id=ids.REFINEMENTS_TABLE)],
            type="circle",
            color="#646569",
        )
    )
