#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import html, DashProxy
import dash_mantine_components as dmc
from automappa.components import ids
from typing import Protocol, List, Literal, Dict


class Scatterplot3dDropdownOptionsDataSource(Protocol):
    def get_scatterplot_3d_zaxis_dropdown_options(
        self,
    ) -> List[Dict[Literal["label", "value"], str]]:
        ...


def render(app: DashProxy, source: Scatterplot3dDropdownOptionsDataSource) -> html.Div:
    options = source.get_scatterplot_3d_zaxis_dropdown_options()
    radio_items = [
        dmc.Radio(option["label"], value=option["value"], color="orange")
        for option in options
    ]
    return html.Div(
        [
            html.Label("Z-axis:"),
            dmc.RadioGroup(
                radio_items,
                id=ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN,
                value=ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN_VALUE_DEFAULT,
                spacing="xs",
                size="sm",
                orientation="vertical",
            ),
        ]
    )
