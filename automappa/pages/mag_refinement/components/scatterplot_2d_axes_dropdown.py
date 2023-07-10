#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import DashProxy, dcc, html, Input, Output
from automappa.components import ids


class Scatterplot2dAxesDropdownDataSource(Protocol):
    def get_scatterplot_2d_axes_options(
        self, metagenome_id: int
    ) -> List[Dict[Literal["label", "value", "disabled"], str]]:
        ...


def render(app: DashProxy, source: Scatterplot2dAxesDropdownDataSource) -> html.Div:
    @app.callback(
        Output(ids.AXES_2D_DROPDOWN, "options"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        # Input(ids.KMER_SIZE_DROPDOWN, "value"),
        # Input(ids.NORM_METHOD_DROPDOWN, "value"),
    )
    def axes_2d_options_callback(
        metagenome_id: int,
        # kmer_size_dropdown_value: int,
        # norm_method_dropdown_value: str,
    ) -> List[Dict[str, str]]:
        return source.get_scatterplot_2d_axes_options(metagenome_id)

    return html.Div(
        [
            html.Label("Axes:"),
            dcc.Dropdown(
                id=ids.AXES_2D_DROPDOWN,
                value=ids.AXES_2D_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
