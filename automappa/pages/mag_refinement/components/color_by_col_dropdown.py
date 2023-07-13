# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import DashProxy, html
import dash_mantine_components as dmc

from automappa.components import ids


class ColorByColDropdownDataSource(Protocol):
    def get_color_by_column_options(self) -> List[Dict[Literal["label", "value"], str]]:
        ...


def render(app: DashProxy, source: ColorByColDropdownDataSource) -> html.Div:
    options = source.get_color_by_column_options()
    radios = [
        dmc.Radio(option["label"], value=option["value"], color="orange")
        for option in options
    ]
    return html.Div(
        [
            html.Label("Color contigs by:"),
            dmc.RadioGroup(
                radios,
                id=ids.COLOR_BY_COLUMN_DROPDOWN,
                value=ids.COLOR_BY_COLUMN_DROPDOWN_VALUE_DEFAULT,
            ),
        ]
    )
