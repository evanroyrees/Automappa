# -*- coding: utf-8 -*-
import logging
from typing import Dict, List
import pandas as pd

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from automappa.components import ids


logger = logging.getLogger(__name__)


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.CYTOSCAPE_SELECT, "data"),
        [Input(ids.SAMPLES_STORE, "data")],
        State(ids.SAMPLES_STORE, "data"),
    )
    def cytoscape_select_options(
        samples_df: pd.DataFrame, new_samples_df: pd.DataFrame
    ) -> List[Dict[str, str]]:
        if samples_df is None or samples_df.empty:
            raise PreventUpdate
        if new_samples_df is not None:
            samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(
                subset=["table_id"]
            )

        if samples_df.empty:
            raise PreventUpdate

        df = samples_df.loc[samples_df.filetype.eq("cytoscape")]
        logger.debug(f"{df.shape[0]:,} cytoscapes available for mag_refinement")
        return [
            {
                "label": filename,
                "value": table_id,
            }
            for filename, table_id in zip(df.filename.tolist(), df.table_id.tolist())
        ]

    return html.Div(
        dmc.Select(
            id=ids.CYTOSCAPE_SELECT,
            label="Cytoscape connections",
            placeholder="Select cytoscape connections annotations",
            icon=[DashIconify(icon="bx:network-chart")],
            rightSection=[DashIconify(icon="radix-icons:chevron-down")],
            persistence=True,
            persistence_type="session",
        )
    )
