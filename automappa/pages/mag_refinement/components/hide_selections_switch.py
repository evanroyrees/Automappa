#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import html
import dash_mantine_components as dmc

from automappa.components import ids


def render() -> html.Div:
    return html.Div(
        dmc.Tooltip(
            label='Toggling this to "On" will hide your manually-curated MAG refinement groups',
            position="bottom-start",
            openDelay=1000,  # milliseconds
            transition="pop-bottom-left",
            transitionDuration=500,
            multiline=True,
            width=300,
            withArrow=True,
            children=[
                dmc.Switch(
                    id=ids.HIDE_SELECTIONS_TOGGLE,
                    checked=ids.HIDE_SELECTIONS_TOGGLE_VALUE_DEFAULT,
                    size="xl",
                    radius="md",
                    color="indigo",
                    label="Hide MAG Refinements",
                    offLabel="Off",
                    onLabel="On",
                )
            ],
        )
    )
