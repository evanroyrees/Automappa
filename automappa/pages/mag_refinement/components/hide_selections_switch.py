#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import html
import dash_mantine_components as dmc

from automappa.components import ids
from automappa.pages.mag_refinement.components import hide_selections_tooltip


def render() -> html.Div:
    return html.Div(
        [
            dmc.Switch(
                id=ids.HIDE_SELECTIONS_TOGGLE,
                checked=ids.HIDE_SELECTIONS_TOGGLE_VALUE_DEFAULT,
                size="xl",
                radius="md",
                color="indigo",
                label="Hide MAG Refinements",
                offLabel="Off",
                onLabel="On",
            ),
            hide_selections_tooltip.render(),
        ]
    )
