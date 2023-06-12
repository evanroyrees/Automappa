#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import html, dcc
from automappa.components import ids


def render() -> html.Div:
    return html.Div(
        [
            html.Label("Z-axis:"),
            dcc.Dropdown(
                id=ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN,
                options=[
                    {"label": "Coverage", "value": "coverage"},
                    {"label": "GC%", "value": "gc_content"},
                    {"label": "Length", "value": "length"},
                ],
                value=ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
