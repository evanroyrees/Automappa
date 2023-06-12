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
        Output(ids.MARKERS_SELECT, "data"),
        [Input(ids.SAMPLES_STORE, "data")],
        State(ids.SAMPLES_STORE, "data"),
    )
    def markers_select_options(
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

        markers_samples = samples_df.loc[samples_df.filetype.eq("markers")]
        logger.debug(
            f"{markers_samples.shape[0]:,} markers available for mag_refinement"
        )
        return [
            {
                "label": filename,
                "value": table_id,
            }
            for filename, table_id in zip(
                markers_samples.filename.tolist(), markers_samples.table_id.tolist()
            )
        ]

    return html.Div(
        dmc.Select(
            id=ids.MARKERS_SELECT,
            label="Markers",
            placeholder="Select marker annotations",
            icon=[DashIconify(icon="line-md:document-report")],
            rightSection=[DashIconify(icon="radix-icons:chevron-down")],
            persistence=True,
            persistence_type="session",
        )
    )
