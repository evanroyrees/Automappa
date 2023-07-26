# -*- coding: utf-8 -*-

from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, State, html, dcc
from automappa.data.source import SampleTables

from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.SELECTED_TABLES_DATATABLE, "children"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
        ],
        State(ids.SELECTED_TABLES_STORE, "data"),
    )
    def selected_tables_datatable_children(
        samples: SampleTables,
        new_tables: SampleTables,
    ):
        if samples is None:
            raise PreventUpdate
        if new_tables is not None:
            if new_tables != samples:
                tables_dict = samples.dict()
                tables_dict.update(new_tables.dict())
                samples = SampleTables.parse_obj(tables_dict)

        has_table = False
        for __, table_id in samples:
            if table_id:
                has_table = True
                break

        if not has_table:
            raise PreventUpdate

        return DataTable(
            data=[
                {"filetype": sample, "table_id": table.id}
                for sample, table in samples
                if sample not in {"kmers"}
            ],
            columns=[
                {"id": "filetype", "name": "filetype", "editable": False},
                {"id": "table_id", "name": "table_id", "editable": False},
            ],
            persistence=True,
            persistence_type="session",
        )

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_SELECTED_TABLES_DATATABLE,
                children=[
                    html.Label("Selected Datasets for Refinement & Summary:"),
                    html.Div(id=ids.SELECTED_TABLES_DATATABLE),
                ],
                type="dot",
                color="#646569",
            ),
        ]
    )
