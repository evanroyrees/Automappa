#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dash_extensions.enrich import html
import dash_mantine_components as dmc
from automappa.components import ids


# Scatterplot 2D Legend Toggle
def render() -> html.Div:
    return html.Div(
        [
            html.Label("Legend"),
            dmc.Switch(
                id=ids.SCATTERPLOT_2D_LEGEND_TOGGLE,
                checked=ids.SCATTERPLOT_2D_LEGEND_TOGGLE_VALUE_DEFAULT,
                size="md",
                color="dark",
                offLabel="off",
                onLabel="on",
                label="Display",
            ),
        ]
    )
