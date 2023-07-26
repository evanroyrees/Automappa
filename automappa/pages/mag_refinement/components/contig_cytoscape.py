from typing import Dict, List, Literal, Optional, Protocol, Union
import dash_cytoscape as cyto
from dash_extensions.enrich import DashProxy, html, Output, Input, dcc

from automappa.components import ids


class ContigCytoscapeDataSource(Protocol):
    def get_cytoscape_elements(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[
        Dict[
            Literal["data"],
            Dict[
                Literal["id", "label", "source", "target", "connections"],
                Union[str, int],
            ],
        ]
    ]:
        ...

    def get_cytoscape_stylesheet(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[
        Dict[
            Literal["selector", "style"],
            Union[Literal["node", "edge"], Dict[str, Union[str, int, float]]],
        ]
    ]:
        ...


def render(app: DashProxy, source: ContigCytoscapeDataSource) -> html.Div:
    @app.callback(
        Output(ids.CONTIG_CYTOSCAPE, "stylesheet"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
        ],
        prevent_initial_call=True,
    )
    def highlight_selected_contigs(
        metagenome_id: int,
        selected_contigs: Dict[str, List[Dict[str, str]]],
    ) -> List[
        Dict[
            Literal["selector", "style"],
            Union[Literal["node", "edge"], Dict[str, Union[str, int, float]]],
        ]
    ]:
        headers = {point["text"] for point in selected_contigs["points"]}
        stylesheet = source.get_cytoscape_stylesheet(metagenome_id, headers)

        SELECTED_COLOR = "#B10DC9"
        stylesheet += [
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
        # TODO
        # 1. Style connections using mappingtype
        # (i.e. differentiate between start and end connections)
        # - https://dash.plotly.com/cytoscape/styling#edge-arrows
        # TODO
        # 2. Add selector based on number of contig connections
        # - https://dash.plotly.com/cytoscape/styling#comparing-data-items-using-selectors
        # It looks like this could be done using the 'weight' key for the edge
        # and then selecting using stylesheet = [{'selector': '[weight > 3]'}]
        # where the '3' could be dynamically updated by a slider component (or other component)
        return stylesheet

    @app.callback(
        Output(ids.CONTIG_CYTOSCAPE, "elements"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
        ],
        prevent_initial_call=True,
    )
    def update_cytoscape_elements(
        metagenome_id: int,
        selected_contigs: Dict[str, List[Dict[str, str]]],
    ) -> List[
        Dict[
            Literal["data"],
            Dict[
                Literal["id", "label", "source", "target", "connections"],
                Union[str, int],
            ],
        ]
    ]:
        headers = {point["text"] for point in selected_contigs["points"]}
        records = source.get_cytoscape_elements(metagenome_id, headers)
        return records

    return html.Div(
        dcc.Loading(
            cyto.Cytoscape(
                id=ids.CONTIG_CYTOSCAPE,
                layout=dict(name="cose"),
                style=dict(width="100%", height="600px"),
                responsive=True,
            ),
            id=ids.LOADING_CONTIG_CYTOSCAPE,
            type="graph",
        ),
    )
