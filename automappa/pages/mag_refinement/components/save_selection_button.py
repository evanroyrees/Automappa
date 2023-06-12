from typing import Dict, List
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from dash_extensions.enrich import DashProxy, html, Output, Input
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_REFINEMENTS_SAVE_BUTTON, "disabled"),
        Input(ids.SCATTERPLOT_2D, "selectedData"),
    )
    def toggle_disabled(
        selected_data: Dict[str, List[Dict[str, str]]],
    ) -> bool:
        return not selected_data

    return html.Div(
        dmc.Button(
            "Save selection to MAG refinement",
            id=ids.MAG_REFINEMENTS_SAVE_BUTTON,
            n_clicks=0,
            size="md",
            leftIcon=[DashIconify(icon="carbon:clean")],
            variant="gradient",
            gradient={"from": "#642E8D", "to": "#1f58a6", "deg": 150},
            disabled=True,
            fullWidth=True,
        )
    )
