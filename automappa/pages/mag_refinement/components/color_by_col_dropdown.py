# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.components import ids


class ColorByColDropdown(Protocol):
    def get_color_by_column_options(
        self, metagenome_id: int
    ) -> List[Dict[Literal["label", "value"], str]]:
        ...


def render(app: DashProxy, source: ColorByColDropdown) -> html.Div:
    @app.callback(
        Output(ids.COLOR_BY_COLUMN_DROPDOWN, "options"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def get_color_options(
        metagenome_id: int,
    ) -> List[Dict[Literal["label", "value"], str]]:
        return source.get_color_by_column_options(metagenome_id)

    return html.Div(
        [
            html.Label("Contigs colored by:"),
            dcc.Dropdown(
                id=ids.COLOR_BY_COLUMN_DROPDOWN,
                options=[],
                value=ids.COLOR_BY_COLUMN_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
