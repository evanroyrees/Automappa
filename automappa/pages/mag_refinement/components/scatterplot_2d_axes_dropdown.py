#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import dcc, html
from automappa.components import ids


scatterplot_2d_axes_dropdown = [
    html.Label("Axes:"),
    dcc.Dropdown(
        id=ids.AXES_2D_DROPDOWN,
        value=ids.AXES_2D_DROPDOWN_VALUE_DEFAULT,
        clearable=False,
    ),
]
