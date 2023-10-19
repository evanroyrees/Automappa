# -*- coding: utf-8 -*-
from typing import Protocol
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.utils.figures import taxonomy_sankey
from automappa.components import ids


class ClusterTaxonomySankeyDataSource(Protocol):
    def get_taxonomy_sankey_records(self, metagenome_id: int, refinement_id: int):
        ...


def render(app: DashProxy, source: ClusterTaxonomySankeyDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_TAXONOMY_SANKEY, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
        prevent_initial_call=True,
    )
    def mag_taxonomy_sankey_callback(
        metagenome_id: int, refinement_id: int
    ) -> go.Figure:
        data = source.get_taxonomy_sankey_records(
            metagenome_id, refinement_id=refinement_id
        )
        fig = taxonomy_sankey(data)
        return fig
    
    graph_config = dict(
        toImageButtonOptions= dict(
            format="svg",
            filename="mag-summary-taxonomy-sankey",
        ),
        displayModeBar='hover',
        displaylogo=False,
        modeBarButtonsToAdd= ['toImage'],
        modeBarButtonsToRemove= ['pan2d','select2d','lasso2d','resetScale2d','zoomOut2d'],
    )

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_TAXONOMY_SANKEY,
                children=[dcc.Graph(id=ids.MAG_TAXONOMY_SANKEY, config=graph_config)],
                type="graph",
            )
        ]
    )
