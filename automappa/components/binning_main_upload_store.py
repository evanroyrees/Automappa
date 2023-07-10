# -*- coding: utf-8 -*-

import logging
from typing import Literal
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, dcc, Serverside

from automappa.data.loader import file_to_db, validate_uploader, create_contigs
from automappa.components import ids
from automappa.data.database import redis_backend

logger = logging.getLogger(__name__)


def render(
    app: DashProxy,
    storage_type: Literal["memory", "session", "local"] = "session",
    clear_data: bool = False,
) -> dcc.Store:
    @app.callback(
        Output(ids.BINNING_MAIN_UPLOAD_STORE, "data"),
        [Input(ids.BINNING_UPLOAD, "isCompleted")],
        [
            State(ids.BINNING_UPLOAD, "fileNames"),
            State(ids.BINNING_UPLOAD, "upload_id"),
        ],
    )
    def on_binning_main_upload(iscompleted, filenames, upload_id):
        try:
            filepath = validate_uploader(iscompleted, filenames, upload_id)
        except ValueError as err:
            logger.warn(err)
            raise PreventUpdate
        if not filepath:
            raise PreventUpdate
        create_contigs(filepath)
        df = file_to_db(
            filepath=filepath,
            filetype="binning",
        )
        return Serverside(df, backend=redis_backend)

    return dcc.Store(
        id=ids.BINNING_MAIN_UPLOAD_STORE,
        storage_type=storage_type,
        clear_data=clear_data,
    )
