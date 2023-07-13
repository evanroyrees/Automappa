#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import DashProxy, dcc, html
import dash_mantine_components as dmc
from automappa.components import ids


class Scatterplot2dAxesDropdownDataSource(Protocol):
    def get_scatterplot_2d_axes_options(
        self,
    ) -> List[Dict[Literal["label", "value", "disabled"], str]]:
        ...


def render(app: DashProxy, source: Scatterplot2dAxesDropdownDataSource) -> html.Div:
    options = [
        dmc.Radio(item["label"], value=item["value"], color="orange")
        for item in source.get_scatterplot_2d_axes_options()
    ]
    return html.Div(
        [
            html.Label("Axes:"),
            dmc.RadioGroup(
                options,
                id=ids.AXES_2D_DROPDOWN,
                value=ids.AXES_2D_DROPDOWN_VALUE_DEFAULT,
                orientation="vertical",
                size="sm",
                spacing="xs",
            ),
        ]
    )
