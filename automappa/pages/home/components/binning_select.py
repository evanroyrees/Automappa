# -*- coding: utf-8 -*-
import logging
import pandas as pd

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, html
import dash_bootstrap_components as dbc

from automappa.components import ids


logger = logging.getLogger(__name__)


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.BINNING_SELECT, "options"),
        [Input(ids.SAMPLES_STORE, "data")],
        State(ids.SAMPLES_STORE, "data"),
    )
    def binning_select_options(samples_df: pd.DataFrame, new_samples_df: pd.DataFrame):
        if samples_df is None or samples_df.empty:
            raise PreventUpdate
        if new_samples_df is not None:
            samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(
                subset=["table_id"]
            )

        if samples_df.empty:
            raise PreventUpdate

        df = samples_df.loc[samples_df.filetype.eq("binning")]
        logger.debug(f"{df.shape[0]:,} binning available for mag_refinement")
        return [
            {
                "label": filename,
                "value": table_id,
            }
            for filename, table_id in zip(df.filename.tolist(), df.table_id.tolist())
        ]

    return html.Div(
        dbc.Select(
            id=ids.BINNING_SELECT,
            placeholder="Select binning annotations",
            persistence=True,
            persistence_type="session",
        ),
    )
