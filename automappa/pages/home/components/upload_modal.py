# -*- coding: utf-8 -*-

from typing import Protocol
from dash_extensions.enrich import DashProxy, Input, Output, State, html

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from automappa.components import ids

from automappa.pages.home.components import upload_stepper


class UploadModalDataSource(Protocol):
    def name_is_unique(self, name: str) -> bool:
        ...


def render(app: DashProxy, source: UploadModalDataSource) -> html.Div:
    @app.callback(
        Output(ids.UPLOAD_MODAL, "is_open"),
        [
            Input(ids.OPEN_MODAL_BUTTON, "n_clicks"),
            Input(ids.CLOSE_MODAL_BUTTON, "n_clicks"),
            Input(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "n_clicks"),
        ],
        [State(ids.UPLOAD_MODAL, "is_open")],
    )
    def toggle_modal(
        open_btn: int,
        close_btn: int,
        submit_btn: int,
        is_open: bool,
    ) -> bool:
        if open_btn or close_btn or submit_btn:
            return not is_open
        return is_open

    # TODO Add text to modal with max_file_size info...
    return html.Div(
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Upload sample annotations"),
                    close_button=False,
                ),
                dbc.ModalBody(upload_stepper.render(app, source)),
                dbc.ModalFooter(
                    dmc.Button(
                        "Close",
                        id=ids.CLOSE_MODAL_BUTTON,
                        leftIcon=[DashIconify(icon="line-md:close-small")],
                        style={"textAlign": "center"},
                        color="dark",
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
