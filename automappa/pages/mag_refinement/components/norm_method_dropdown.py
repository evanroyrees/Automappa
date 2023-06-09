#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import dcc, html
from automappa.components import ids

norm_method_dropdown = [
    html.Label("K-mer norm. method:"),
    dcc.Dropdown(
        id=ids.NORM_METHOD_DROPDOWN,
        options=["am_clr", "ilr"],
        value=ids.NORM_METHOD_DROPDOWN_VALUE_DEFAULT,
        clearable=False,
    ),
]
