# -*- coding: utf-8 -*-

import logging
from typing import List, Literal
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, dcc, Serverside

from automappa.data.loader import (
    file_to_db,
    validate_uploader,
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
        Output(ids.MARKERS_UPLOAD_STORE, "data"),
        [Input(ids.MARKERS_UPLOAD, "isCompleted")],
        [
            State(ids.MARKERS_UPLOAD, "fileNames"),
            State(ids.MARKERS_UPLOAD, "upload_id"),
        ],
    )
    def on_markers_upload(is_completed: bool, filenames: List[str], upload_id: str):
        try:
            filepath = validate_uploader(is_completed, filenames, upload_id)
        except ValueError as err:
            logger.warn(err)
            raise PreventUpdate
        if not filepath:
            raise PreventUpdate
        df = file_to_db(filepath, "markers")
        return Serverside(df, backend=redis_backend)

    return dcc.Store(
        id=ids.MARKERS_UPLOAD_STORE,
        storage_type=storage_type,
        clear_data=clear_data,
    )
