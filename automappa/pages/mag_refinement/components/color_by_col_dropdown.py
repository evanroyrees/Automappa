# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import DashProxy, dcc, html

from automappa.components import ids


class ColorByColDropdownDataSource(Protocol):
    def get_color_by_column_options(self) -> List[Dict[Literal["label", "value"], str]]:
        ...


def render(app: DashProxy, source: ColorByColDropdownDataSource) -> html.Div:
    options = source.get_color_by_column_options()

    return html.Div(
        [
            html.Label("Contigs colored by:"),
            dcc.Dropdown(
                id=ids.COLOR_BY_COLUMN_DROPDOWN,
                options=options,
                value=ids.COLOR_BY_COLUMN_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
