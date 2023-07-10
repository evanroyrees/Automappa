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
    # @app.callback(
    #     Output(ids.OPEN_MODAL_BUTTON, "disabled"),
    #     Input(ids.SAMPLE_CARDS_CONTAINER, "children")
    # )
    # def disable_during_db_ingest(sample_card: List[dmc.Card]):
    #     # TODO Determine how to get loading state of most recent sample card
    #     return

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
