from typing import Dict, List, Protocol
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from dash_extensions.enrich import DashProxy, html, Output, Input
from automappa.components import ids


class SaveSelectionButtonDataSource(Protocol):
    def save_selections_to_refinement(
        self, metagenome_id: int, headers: List[str]
    ) -> None:
        ...


def render(app: DashProxy, source: SaveSelectionButtonDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_REFINEMENTS_SAVE_BUTTON, "disabled"),
        Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
    )
    def disable_save_button(
        selected_data: Dict[str, List[Dict[str, str]]],
    ) -> bool:
        if (
            selected_data
            and len({point["text"] for point in selected_data["points"]}) > 0
        ):
            return False
        return True

    @app.callback(
        Output(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
            Input(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def store_binning_refinement_selections(
        metagenome_id: int,
        selected_data: Dict[str, List[Dict[str, str]]],
        n_clicks: int,
    ) -> int:
        # Initial load...
        if not n_clicks or (n_clicks and not selected_data) or not selected_data:
            raise PreventUpdate
        headers = {point["text"] for point in selected_data["points"]}
        source.save_selections_to_refinement(
            metagenome_id=metagenome_id, headers=headers
        )
        return 0

    return html.Div(
        dmc.Tooltip(
            dmc.Button(
                "Save MAG",
                id=ids.MAG_REFINEMENTS_SAVE_BUTTON,
                n_clicks=0,
                size="md",
                leftIcon=[DashIconify(icon="carbon:clean")],
                variant="gradient",
                gradient={"from": "#642E8D", "to": "#1f58a6", "deg": 150},
                disabled=True,
                fullWidth=True,
            ),
            label="Save selection to MAG refinement",
            transitionDuration=500,
            openDelay=1500,
            transition="fade",
        )
    )
