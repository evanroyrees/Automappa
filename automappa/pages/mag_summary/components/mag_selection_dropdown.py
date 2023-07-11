# -*- coding: utf-8 -*-

from typing import Dict, List, Protocol, Literal
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.components import ids


class ClusterSelectionDropdownOptionsDataSource(Protocol):
    def get_cluster_selection_dropdown_options(
        self, metagenome_id: int
    ) -> List[Dict[Literal["label", "value"], str]]:
        ...


def render(
    app: DashProxy, source: ClusterSelectionDropdownOptionsDataSource
) -> html.Div:
    @app.callback(
        Output(ids.MAG_SELECTION_DROPDOWN, "options"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def mag_selection_dropdown_options_callback(
        metagenome_id: int,
    ) -> List[Dict[Literal["label", "value"], str]]:
        options = source.get_cluster_selection_dropdown_options(metagenome_id)
        return options

    return html.Div(
        [
            html.Label("MAG Selection Dropdown"),
            dcc.Dropdown(
                id=ids.MAG_SELECTION_DROPDOWN,
                clearable=True,
                placeholder="Select a MAG from this dropdown for a MAG-specific summary",
            ),
        ]
    )
