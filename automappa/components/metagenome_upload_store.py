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
from automappa.data.db import file_system_backend


logger = logging.getLogger(__name__)


def render(
    app: DashProxy,
    storage_type: Literal["memory", "session", "local"] = "session",
    clear_data: bool = False,
) -> dcc.Store:
    """_summary_

    Note
    ----
    For information on the dash_uploader component and callbacks...
    See https://github.com/np-8/dash-uploader#example-with-callback-and-other-options

    Parameters
    ----------
    app : DashProxy
        _description_
    storage_type : Literal[&quot;memory&quot;, &quot;session&quot;, &quot;local&quot;], optional
        _description_, by default "session"
    clear_data : bool, optional
        _description_, by default False

    Returns
    -------
    dcc.Store
        _description_

    Raises
    ------
    PreventUpdate
        _description_
    PreventUpdate
        _description_
    """

    @app.callback(
        Output(ids.METAGENOME_UPLOAD_STORE, "data"),
        [Input(ids.UPLOAD_METAGENOME_DATA, "isCompleted")],
        [
            State(ids.UPLOAD_METAGENOME_DATA, "fileNames"),
            State(ids.UPLOAD_METAGENOME_DATA, "upload_id"),
        ],
    )
    def on_metagenome_upload(iscompleted, filenames, upload_id):
        try:
            filepath = validate_uploader(iscompleted, filenames, upload_id)
        except ValueError as err:
            logger.warn(err)
            raise PreventUpdate
        if not filepath:
            raise PreventUpdate
        df = file_to_db(filepath, "metagenome")
        return Serverside(df, backend=file_system_backend)

    return dcc.Store(
        id=ids.METAGENOME_UPLOAD_STORE,
        storage_type=storage_type,
        clear_data=clear_data,
    )
