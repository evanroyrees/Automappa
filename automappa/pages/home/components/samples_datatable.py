# -*- coding: utf-8 -*-

import logging
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, State, html, dcc
import pandas as pd

from automappa.components import ids


logger = logging.getLogger(__name__)


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.SAMPLES_DATATABLE, "children"),
        [Input(ids.SAMPLES_STORE, "data")],
        State(ids.SAMPLES_STORE, "data"),
    )
    def on_samples_store_data(samples_df: pd.DataFrame, new_samples_df: pd.DataFrame):
        if samples_df is None or samples_df.empty:
            raise PreventUpdate
        if new_samples_df is not None:
            samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(
                subset=["table_id"]
            )

        logger.debug(f"retrieved {samples_df.shape[0]:,} samples from samples store")

        if samples_df.empty:
            raise PreventUpdate

        return DataTable(
            data=samples_df.to_dict("records"),
            columns=[
                {"id": col, "name": col, "editable": False}
                for col in samples_df.columns
            ],
            persistence=True,
            persistence_type="session",
        )

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_SAMPLES_DATATABLE,
                children=[
                    html.Label("Uploaded Datasets"),
                    html.Div(id=ids.SAMPLES_DATATABLE),
                ],
                type="dot",
                color="#646569",
            ),
        ]
    )
