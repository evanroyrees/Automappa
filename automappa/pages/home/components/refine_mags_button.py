# -*- coding: utf-8 -*-

import logging
from dash_extensions.enrich import DashProxy, Input, Output, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from automappa.components import ids


logger = logging.getLogger(__name__)


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.REFINE_MAGS_BUTTON, "disabled"),
        [
            Input(ids.BINNING_SELECT, "value"),
            Input(ids.MARKERS_SELECT, "value"),
            Input(ids.METAGENOME_SELECT, "value"),
        ],
    )
    def disable_button_callback(
        binning_value: str, markers_value: str, metagenome_value: str
    ) -> bool:
        return (
            binning_value is None or markers_value is None or metagenome_value is None
        )

    return html.Div(
        dmc.Button(
            "Refine MAGs",
            id=ids.REFINE_MAGS_BUTTON,
            leftIcon=[DashIconify(icon="mingcute:broom-line", width=25)],
            variant="gradient",
            gradient={"from": "#642E8D", "to": "#1f58a6", "deg": 150},
            fullWidth=True,
        )
    )
