# -*- coding: utf-8 -*-
from typing import Protocol
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from plotly import graph_objects as go

from automappa.utils.figures import taxonomy_sankey
from automappa.components import ids


class ClusterTaxonomySankeyDataSource(Protocol):
    def get_taxonomy_sankey_records(self, metagenome_id: int, cluster: str):
        ...


def render(app: DashProxy, source: ClusterTaxonomySankeyDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_TAXONOMY_SANKEY, "figure"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.MAG_SELECTION_DROPDOWN, "value"),
    )
    def mag_taxonomy_sankey_callback(metagenome_id: int, cluster: str) -> go.Figure:
        data = source.get_taxonomy_sankey_records(metagenome_id, cluster=cluster)
        fig = taxonomy_sankey(data)
        return fig

    return html.Div(
        children=[
            dcc.Loading(
                id=ids.LOADING_MAG_TAXONOMY_SANKEY,
                children=[dcc.Graph(id=ids.MAG_TAXONOMY_SANKEY)],
                type="graph",
            )
        ]
    )
