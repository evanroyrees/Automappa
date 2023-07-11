#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Protocol
from dash_extensions.enrich import html, Input, Output, DashProxy
import dash_mantine_components as dmc

from automappa.components import ids


class HideRefinementsSwitchDataSource(Protocol):
    def has_user_refinements(self, metagenome_id: int) -> bool:
        ...


def render(app: DashProxy, source: HideRefinementsSwitchDataSource) -> html.Div:
    @app.callback(
        Output(ids.HIDE_SELECTIONS_TOGGLE, "disabled"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def disable_switch(metagenome_id: int) -> bool:
        return not source.has_user_refinements(metagenome_id)

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
