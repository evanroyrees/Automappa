# -*- coding: utf-8 -*-

import logging
from typing import List, Protocol
from uuid import UUID
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, dcc, html
import dash_uploader as du

from automappa.components import ids

logger = logging.getLogger(__name__)


class UploadDataSource(Protocol):
    def validate_uploader_path(
        self, is_completed: bool, filenames: List[str], upload_id: UUID
    ) -> str:
        ...


def render(app: DashProxy, source: UploadDataSource) -> html.Div:
    @app.callback(
        Output(ids.METAGENOME_UPLOAD_STORE, "data"),
        Input(ids.METAGENOME_UPLOAD, "isCompleted"),
        State(ids.METAGENOME_UPLOAD, "fileNames"),
        State(ids.METAGENOME_UPLOAD, "upload_id"),
        prevent_initial_call=True,
    )
    def on_metagenome_upload(is_completed: bool, filenames: List[str], upload_id: UUID):
        if not is_completed:
            raise PreventUpdate
        try:
            filepath = source.validate_uploader_path(is_completed, filenames, upload_id)
        except ValueError as err:
            logger.warn(err)
            raise PreventUpdate
        if not filepath:
            raise PreventUpdate
        return filepath

    return html.Div(
        [
            dcc.Store(
                id=ids.METAGENOME_UPLOAD_STORE,
                storage_type="session",
                clear_data=False,
            ),
            du.Upload(
                id=ids.METAGENOME_UPLOAD,
                text="Drag and Drop or Select metagenome assembly",
                default_style={
                    "width": "100%",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "margin": "10px",
                },
                max_files=1,
                max_file_size=10240,
            ),
        ]
    )
