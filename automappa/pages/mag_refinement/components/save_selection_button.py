from typing import Dict, List
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from dash_extensions.enrich import DashProxy, html, Output, Input
from automappa.components import ids
from automappa.data.loader import table_to_db
from automappa.data.source import SampleTables


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_REFINEMENTS_SAVE_BUTTON, "disabled"),
        Input(ids.SCATTERPLOT_2D, "selectedData"),
    )
    def toggle_disabled(
        selected_data: Dict[str, List[Dict[str, str]]],
    ) -> bool:
        return not selected_data

    @app.callback(
        Output(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        [
            Input(ids.SCATTERPLOT_2D, "selectedData"),
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        ],
    )
    def store_binning_refinement_selections(
        selected_data: Dict[str, List[Dict[str, str]]],
        sample: SampleTables,
        n_clicks: int,
    ) -> int:
        # Initial load...
        if not n_clicks or (n_clicks and not selected_data) or not selected_data:
            raise PreventUpdate
        bin_df = sample.refinements.table
        refinement_cols = [col for col in bin_df.columns if "refinement" in col]
        refinement_num = len(refinement_cols) + 1
        refinement_name = f"refinement_{refinement_num}"
        contigs = list({point["text"] for point in selected_data["points"]})
        bin_df.loc[contigs, refinement_name] = refinement_name
        bin_df = bin_df.fillna(axis="columns", method="ffill")
        bin_df.reset_index(inplace=True)
        table_to_db(df=bin_df, name=sample.refinements.id)
        return 0

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
