# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, State, html

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_uploader as du

from automappa.components import ids


binning_main_upload = du.Upload(
    id=ids.UPLOAD_BINNING_MAIN_DATA,
    text="Drag and Drop or Select binning-main file",
    default_style={
        "width": "100%",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "margin": "10px",
    },
    max_files=1,
    max_file_size=10240,
)

markers_upload = du.Upload(
    id=ids.UPLOAD_MARKERS_DATA,
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
)

metagenome_upload = du.Upload(
    id=ids.UPLOAD_METAGENOME_DATA,
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
)

cytoscape_connection_upload = du.Upload(
    id=ids.UPLOAD_CYTOSCAPE_DATA,
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
)


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.UPLOAD_MODAL, "is_open"),
        [
            Input(ids.OPEN_MODAL_BUTTON, "n_clicks"),
            Input(ids.CLOSE_MODAL_BUTTON, "n_clicks"),
        ],
        [State(ids.UPLOAD_MODAL, "is_open")],
    )
    def toggle_modal(n_open, n_close, is_open):
        if n_open or n_close:
            return not is_open
        return is_open

    # TODO: Add text to modal with max_file_size info...
    return html.Div(
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Upload Metagenome annotations"),
                    close_button=False,
                ),
                dbc.ModalBody(
                    [
                        binning_main_upload,
                        markers_upload,
                        metagenome_upload,
                        cytoscape_connection_upload,
                    ]
                ),
                dbc.ModalFooter(
                    dmc.Button(
                        "Close",
                        id=ids.CLOSE_MODAL_BUTTON,
                        leftIcon=[DashIconify(icon="line-md:close-small")],
                        style={"textAlign": "center"},
                        color="dark",
                        fullWidth=True,
                    )
                ),
            ],
            id=ids.UPLOAD_MODAL,
            keyboard=False,
            backdrop="static",
            size="lg",
            fullscreen=False,
            centered=True,
        ),
    )
