import logging
from typing import List, Protocol
from uuid import UUID
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, State, dcc, html
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
        Output(ids.CYTOSCAPE_STORE, "data"),
        Input(ids.CYTOSCAPE_UPLOAD, "isCompleted"),
        State(ids.CYTOSCAPE_UPLOAD, "fileNames"),
        State(ids.CYTOSCAPE_UPLOAD, "upload_id"),
        prevent_initial_call=True,
    )
    def cytoscape_uploader_callback(
        is_completed: bool, filenames: List[str], upload_id: UUID
    ):
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
                id=ids.CYTOSCAPE_STORE,
                storage_type="session",
                clear_data=False,
            ),
            du.Upload(
                id=ids.CYTOSCAPE_UPLOAD,
                text="Drag and Drop or Select cytoscape contig connections file",
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
