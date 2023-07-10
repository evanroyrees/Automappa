#!/usr/bin/env python
# -*- coding: utf-8 -*-


import dash_ag_grid as dag
from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.components import ids


class RefinementsTableDataSource(Protocol):
    def get_refinements_row_data(
        self, metagenome_id: int
    ) -> List[Dict[Literal["contig", "cluster"], str]]:
        ...


def render(app: DashProxy, source: RefinementsTableDataSource) -> html.Div:
    @app.callback(
        Output(ids.REFINEMENTS_TABLE, "rowData"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        ],
    )
    def refinements_table_callback(
        metagenome_id: int,
        btn_clicks: int,
    ) -> List[Dict[Literal["contig", "cluster"], str]]:
        row_data = source.get_refinements_row_data(metagenome_id)

        return row_data

    column_defs = [
        {"field": "contig", "headerName": "Contig", "resizable": True},
        {"field": "cluster", "headerName": "Cluster"},
    ]

    return html.Div(
        [
            html.Label("Table 2. MAG Refinements"),
            dcc.Loading(
                dag.AgGrid(
                    id=ids.REFINEMENTS_TABLE,
                    className="ag-theme-material",
                    columnSize="responsiveSizetoFit",
                    style=dict(height=600, width="100%"),
                    columnDefs=column_defs,
                ),
                id=ids.LOADING_REFINEMENTS_TABLE,
                type="circle",
                color="#646569",
            ),
        ]
    )
