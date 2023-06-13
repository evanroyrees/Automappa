from typing import Dict, List, Union
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, html, Output, Input
import pandas as pd
import dash_cytoscape as cyto
from automappa.components import ids
from automappa.data.source import SampleTables


def render(app: DashProxy) -> html.Div:
    # @app.callback(
    #     Output(ids.CONTIG_CYTOSCAPE, "stylesheet"),
    #     # Not sure which property should be updated here
    #     # Using "stylesheet" as placeholder
    #     # Cytoscape property reference list: https://dash.plotly.com/cytoscape/reference
    #     Input(ids.SCATTERPLOT_2D, "selectedData"),
    # )
    # def highlight_selected_contigs(selected_contigs: Dict[str, List[Dict[str, str]]]):
    #     if not selected_contigs:
    #         raise PreventUpdate
    #     contigs = {point["text"] for point in selected_contigs["points"]}
    #     raise NotImplemented

    # NOTE: Multiple callbacks may be registered if other Outputs/Inputs are desired
    @app.callback(
        Output(ids.CONTIG_CYTOSCAPE, "elements"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
    )
    def cytoscape_callback(
        sample: SampleTables,
    ) -> List[Dict[str, Dict[str, Union[str, int, float]]]]:
        cyto_df = sample.cytoscape.table
        # TODO: Implement cytoscape callback...
        return [
            {
                "data": {"id": "one", "label": "Node 1"},
                "position": {"x": 75, "y": 75},
            },
            {
                "data": {"id": "two", "label": "Node 2"},
                "position": {"x": 200, "y": 200},
            },
            {"data": {"source": "one", "target": "two"}},
        ]

    return html.Div(
        cyto.Cytoscape(
            id=ids.CONTIG_CYTOSCAPE,
            layout={"name": "preset"},
            style={"width": "100%", "height": "600px"},
            # NOTE: NOT sure why but "height" here seems necessary as
            # without it the component does not render...
            # W/o any styling the component only renders 1/3 of the browser width...
            # This is NOT preferred as layout is being handled using dbc and should
            # follow whatever is specified... :shrug:
            responsive=True,
        )
    )
