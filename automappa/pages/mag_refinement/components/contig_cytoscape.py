from typing import Dict, List, Union
from dash.exceptions import PreventUpdate
import dash_cytoscape as cyto
from dash_extensions.enrich import DashProxy, html, Output, Input, dcc

from automappa.components import ids
from automappa.data.source import SampleTables


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.CONTIG_CYTOSCAPE, "stylesheet"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.SCATTERPLOT_2D, "selectedData"),
        ],
    )
    def highlight_selected_contigs(
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
        stylesheet = [
            {
                "selector": "node",
                "style": {"label": "data(label)", "opacity": 0.7},
            },
            {
                "selector": "edge",
                "style": {
                    "opacity": 0.4,
                    "curve-style": "bezier",
                    "label": "data(connections)",
                },
            },
        ]

        for contigs in contigs:
            if contigs in cyto_df["node1"].values or (
                contigs in cyto_df["node2"].values
            ):
                stylesheet.append(
                    {
                        "selector": f"[label = '{contigs}']",
                        "style": {"background-color": "#B10DC9", "opacity": 0.8},
                    }
                )
            stylesheet.append(
                {"selector": "edge", "style": {"width": "data(connections)"}}
            )
        return stylesheet

    @app.callback(
        Output(ids.CONTIG_CYTOSCAPE, "elements"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.SCATTERPLOT_2D, "selectedData"),
        ],
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
        for source, target, connections in zip(
            cyto_df.node1, cyto_df.node2, cyto_df.connections
        ):
            if source not in nodes:
                nodes.add(source)
                cy_nodes.append({"data": {"id": source, "label": source}})
            if target not in nodes:
                nodes.add(target)
                cy_nodes.append({"data": {"id": target, "label": target}})
            cy_edges.append(
                {
                    "data": {
                        "source": source,
                        "target": target,
                        "connections": connections,
                    }
                }
            )
        return cy_edges + cy_nodes

    return html.Div(
        dcc.Loading(
            cyto.Cytoscape(
                id=ids.CONTIG_CYTOSCAPE,
                layout={"name": "cose"},
                style={"width": "100%", "height": "600px"},
                stylesheet=[
                    {
                        "selector": "node",
                        "style": {"label": "data(label)", "opacity": 0.7},
                    },
                    {
                        "selector": "edge",
                        "style": {
                            "opacity": 0.4,
                            "curve-style": "bezier",
                        },
                    },
                ],
                responsive=True,
            ),
            id=ids.LOADING_CONTIG_CYTOSCAPE,
            type="graph",
        ),
    )
