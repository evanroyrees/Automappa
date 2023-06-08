# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.data.source import SampleTables
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.COLOR_BY_COLUMN_DROPDOWN, "options"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
    )
    def get_color_options(sample: SampleTables):
        df = sample.binning.table
        return [
            {"label": col.title().replace("_", " "), "value": col}
            for col in df.select_dtypes("object").columns
        ]

    return html.Div(
        [
            html.Label("Contigs colored by:"),
            dcc.Dropdown(
                id=ids.COLOR_BY_COLUMN_DROPDOWN,
                options=[],
                value=ids.COLOR_BY_COLUMN_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
