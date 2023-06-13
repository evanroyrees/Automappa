from typing import Dict, List, Union
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, html, Output, Input
import pandas as pd
import dash_cytoscape as cyto
from automappa.components import ids
from automappa.data.source import SampleTables


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.CONTIG_CYTOSCAPE, "elements"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.SCATTERPLOT_2D, "selectedData"),
    )
    def cytoscape_callback(
        sample: SampleTables,
        selected_contigs: Dict[str, List[Dict[str, str]]],
    ) -> List[Dict[str, Dict[str, Union[str, int, float]]]]:
        if not selected_contigs:
            raise PreventUpdate
        contigs = {point["text"] for point in selected_contigs["points"]}
        cyto_df = sample.cytoscape.table
        contigs_regstr = "|".join(contigs)
        cyto_df = cyto_df[
            cyto_df.node1.str.contains(contigs_regstr)
            | cyto_df.node2.str.contains(contigs_regstr)
        ]
        nodes = set()
        cy_edges = []
        cy_nodes = []
        for source, target in zip(cyto_df.node1, cyto_df.node2):
            if source not in nodes:
                nodes.add(source)
                cy_nodes.append({"data": {"id": source, "label": source}})
            if target not in nodes:
                nodes.add(target)
                cy_nodes.append({"data": {"id": target, "label": target}})
            cy_edges.append({"data": {"source": source, "target": target}})
        elements = cy_edges + cy_nodes
        return elements

    return html.Div(
        cyto.Cytoscape(
            id=ids.CONTIG_CYTOSCAPE,
            layout={"name": "grid"},
            style={"width": "100%", "height": "600px"},
            # NOTE: NOT sure why but "height" here seems necessary as
            # without it the component does not render...
            # W/o any styling the component only renders 1/3 of the browser width...
            # This is NOT preferred as layout is being handled using dbc and should
            # follow whatever is specified... :shrug:
            responsive=True,
        )
    )
