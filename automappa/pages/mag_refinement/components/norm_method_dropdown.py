#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import dcc, html
from automappa.components import ids


def render() -> html.Div:
    return html.Div(
        [
            html.Label("norm. method:"),
            dcc.Dropdown(
                id=ids.NORM_METHOD_DROPDOWN,
                options=[
                    dict(label="CLR", value="am_clr"),
                    dict(label="ILR", value="ilr"),
                ],
                value=ids.NORM_METHOD_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
