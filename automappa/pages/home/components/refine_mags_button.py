# -*- coding: utf-8 -*-

import logging
from dash_extensions.enrich import DashProxy, Input, Output, html
import dash_bootstrap_components as dbc

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
    def disable_button_callback(binning_value, markers_value, metagenome_value):
        if binning_value is None or markers_value is None or metagenome_value is None:
            return True
        else:
            return False

    return html.Div(
        children=[
            dbc.Button(
                id=ids.REFINE_MAGS_BUTTON,
                children="Refine MAGs",
            )
        ]
    )
