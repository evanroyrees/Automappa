#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import DashProxy, dcc, html, Input, Output
from automappa.components import ids


class Scatterplot2dAxesDropdownDataSource(Protocol):
    def get_scatterplot_2d_axes_options(
        self,
    ) -> List[Dict[Literal["label", "value", "disabled"], str]]:
        ...


def render(app: DashProxy, source: Scatterplot2dAxesDropdownDataSource) -> html.Div:
    options = source.get_scatterplot_2d_axes_options()
    return html.Div(
        [
            html.Label("Axes:"),
            dcc.Dropdown(
                id=ids.AXES_2D_DROPDOWN,
                options=options,
                value=ids.AXES_2D_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
