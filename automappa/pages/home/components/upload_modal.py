# -*- coding: utf-8 -*-


from dash_extensions.enrich import DashProxy, Input, Output, State, html

import dash_bootstrap_components as dbc
import dash_uploader as du

from automappa.components import ids


binning_main_upload = du.Upload(
    id=ids.UPLOAD_BINNING_MAIN_DATA,
    text="Drag and Drop or Select binning-main file",
    default_style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    max_files=1,
    # 10240 MB = 10GB
    # TODO: Add text to modal with max_file_size info...
    max_file_size=10240,
)

markers_upload = du.Upload(
    id=ids.UPLOAD_MARKERS_DATA,
    text="Drag and Drop or Select marker annotations file",
    default_style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    max_files=1,
    # 10240 MB = 10GB
    # TODO: Add text to modal with max_file_size info...
    max_file_size=10240,
)

metagenome_upload = du.Upload(
    id=ids.UPLOAD_METAGENOME_DATA,
    text="Drag and Drop or Select metagenome assembly",
    default_style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    max_files=1,
    # 10240 MB = 10GB
    # TODO: Add text to modal with max_file_size info...
    max_file_size=10240,
)


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MODAL_DISMISS, "is_open"),
        [Input(ids.OPEN_DISMISS, "n_clicks"), Input(ids.CLOSE_DISMISS, "n_clicks")],
        [State(ids.MODAL_DISMISS, "is_open")],
    )
    def toggle_modal(n_open, n_close, is_open):
        if n_open or n_close:
            return not is_open
        return is_open

    return html.Div(
        children=[
            dbc.Button("Upload data", id=ids.OPEN_DISMISS),
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
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id=ids.CLOSE_DISMISS, style={"textAlign": "center"}
                        )
                    ),
                ],
                id=ids.MODAL_DISMISS,
                keyboard=False,
                backdrop="static",
                fullscreen=True,
            ),
        ],
    )
