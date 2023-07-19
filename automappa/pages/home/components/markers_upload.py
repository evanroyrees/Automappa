# -*- coding: utf-8 -*-

import logging
from typing import List, Protocol
from uuid import UUID
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, DashProxy, dcc, html
from automappa.components import ids

import dash_uploader as du

logger = logging.getLogger(__name__)


class UploadDataSource(Protocol):
    def validate_uploader_path(
        self, is_completed: bool, filenames: List[str], upload_id: UUID
    ) -> str:
        ...


def render(app: DashProxy, source: UploadDataSource) -> html.Div:
    @app.callback(
        Output(ids.MARKERS_UPLOAD_STORE, "data"),
        Input(ids.MARKERS_UPLOAD, "isCompleted"),
        State(ids.MARKERS_UPLOAD, "fileNames"),
        State(ids.MARKERS_UPLOAD, "upload_id"),
        prevent_initial_call=True,
    )
    def on_markers_upload(is_completed: bool, filenames: List[str], upload_id: UUID):
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
                id=ids.MARKERS_UPLOAD_STORE,
                storage_type="session",
                clear_data=False,
            ),
            du.Upload(
                id=ids.MARKERS_UPLOAD,
                text="Drag and Drop or Select marker annotations file",
                default_style={
                    "width": "100%",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "margin": "10px",
                },
                max_files=1,
                # 10240 MB = 10GB
                max_file_size=10240,
            ),
        ]
    )
