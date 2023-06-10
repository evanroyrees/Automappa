# -*- coding: utf-8 -*-

from dash_iconify import DashIconify
from dash_extensions.enrich import DashProxy, html

import dash_mantine_components as dmc

from automappa.components import ids
from automappa.pages.home.components import upload_modal


def render(app: DashProxy) -> html.Div:
    return html.Div(
        [
            dmc.Button(
                "Upload data",
                id=ids.OPEN_DISMISS,
                leftIcon=[DashIconify(icon="line-md:upload-outline")],
                variant="gradient",
                gradient={"from": "#CA2270", "to": "#F36E2D"},
            ),
            upload_modal.render(app),
        ]
    )
