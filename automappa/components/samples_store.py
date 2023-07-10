# -*- coding: utf-8 -*-

import logging
from typing import Literal
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, dcc, Serverside
import pandas as pd

from automappa.data.loader import (
    get_uploaded_files_table,
)
from automappa.components import ids
from automappa.data.database import redis_backend

logger = logging.getLogger(__name__)


def render(
    app: DashProxy,
    storage_type: Literal["memory", "session", "local"] = "session",
    clear_data: bool = False,
) -> dcc.Store:
    @app.callback(
        Output(ids.SAMPLES_STORE, "data"),
        [
            Input(ids.BINNING_MAIN_UPLOAD_STORE, "modified_timestamp"),
            Input(ids.MARKERS_UPLOAD_STORE, "modified_timestamp"),
            Input(ids.METAGENOME_UPLOAD_STORE, "modified_timestamp"),
            Input(ids.CYTOSCAPE_STORE, "modified_timestamp"),
        ],
        [
            State(ids.BINNING_MAIN_UPLOAD_STORE, "data"),
            State(ids.MARKERS_UPLOAD_STORE, "data"),
            State(ids.METAGENOME_UPLOAD_STORE, "data"),
            State(ids.CYTOSCAPE_STORE, "data"),
            State(ids.SAMPLES_STORE, "data"),
        ],
    )
    def on_upload_stores_data(
        binning_uploads_timestamp: str,
        markers_uploads_timestamp: str,
        metagenome_uploads_timestamp: str,
        cytoscape_uploads_timestamp: str,
        binning_uploads_df: pd.DataFrame,
        markers_uploads_df: pd.DataFrame,
        metagenome_uploads_df: pd.DataFrame,
        cytoscape_uploads_df: pd.DataFrame,
        samples_store_data_df: pd.DataFrame,
    ):
        if (
            binning_uploads_df is None
            and markers_uploads_df is None
            and metagenome_uploads_df is None
            and cytoscape_uploads_df is None
        ) or (
            binning_uploads_timestamp is None
            and markers_uploads_timestamp is None
            and metagenome_uploads_timestamp is None
            and cytoscape_uploads_timestamp is None
        ):
            # Check if db has any samples in table
            uploaded_files_df = get_uploaded_files_table()
            if not uploaded_files_df.empty:
                return Serverside(uploaded_files_df, backend=redis_backend)
            raise PreventUpdate
        samples_df = pd.concat(
            [
                binning_uploads_df,
                markers_uploads_df,
                metagenome_uploads_df,
                cytoscape_uploads_df,
                samples_store_data_df,
            ]
        ).drop_duplicates(subset=["table_id"])
        logger.debug(
            f"{samples_df.shape[0]:,} samples retrieved from data upload stores"
        )
        return Serverside(samples_df, backend=redis_backend)

    return dcc.Store(
        id=ids.SAMPLES_STORE,
        storage_type=storage_type,
        clear_data=clear_data,
    )
