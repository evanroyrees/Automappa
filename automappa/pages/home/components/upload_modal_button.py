# -*- coding: utf-8 -*-

from typing import List, Protocol
from dash_iconify import DashIconify
from dash_extensions.enrich import DashProxy, html, Output, Input

import dash_mantine_components as dmc

from automappa.components import ids
from automappa.pages.home.components import upload_modal


class UploadModalButtonDataSource(Protocol):
    def name_is_unique(self, name: str) -> bool:
        ...


def render(app: DashProxy, source: UploadModalButtonDataSource) -> html.Div:
    @app.callback(
        Output(ids.OPEN_MODAL_BUTTON, "disabled"),
        Input(ids.TASK_ID_STORE, "data"),
    )
    def disable_task_button(task_ids: List[str]) -> bool:
        return True if task_ids and task_ids is not None else False

    return html.Div(
        [
            dmc.Button(
                "New Sample",
                id=ids.OPEN_MODAL_BUTTON,
                leftIcon=[DashIconify(icon="line-md:upload-outline", width=25)],
                variant="gradient",
                gradient={"from": "#CA2270", "to": "#F36E2D"},
                fullWidth=False,
            ),
            upload_modal.render(app, source),
        ]
    )
