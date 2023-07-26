#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash_mantine_components as dmc
from dash_extensions.enrich import html
from automappa.components import ids


# Scatterplot 3D Legend Toggle
def render() -> html.Div:
    return html.Div(
        [
            html.Label("Legend"),
            dmc.Switch(
                id=ids.SCATTERPLOT_3D_LEGEND_TOGGLE,
                checked=ids.SCATTERPLOT_2D_LEGEND_TOGGLE_VALUE_DEFAULT,
                size="md",
                color="dark",
                offLabel="off",
                onLabel="on",
                label="Display",
            ),
        ]
    )
