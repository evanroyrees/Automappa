# -*- coding: utf-8 -*-

import logging
from typing import Literal
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, dcc, Serverside

from automappa.data.loader import (
    file_to_db,
    validate_uploader,
)
from automappa.components import ids
from automappa.data.db import redis_backend

logger = logging.getLogger(__name__)


def render(
    app: DashProxy,
    storage_type: Literal["memory", "session", "local"] = "session",
    clear_data: bool = False,
) -> dcc.Store:
    @app.callback(
        Output(ids.MARKERS_UPLOAD_STORE, "data"),
        [Input(ids.UPLOAD_MARKERS_DATA, "isCompleted")],
        [
            State(ids.UPLOAD_MARKERS_DATA, "fileNames"),
            State(ids.UPLOAD_MARKERS_DATA, "upload_id"),
        ],
    )
    def on_markers_upload(iscompleted, filenames, upload_id):
        try:
            filepath = validate_uploader(iscompleted, filenames, upload_id)
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
