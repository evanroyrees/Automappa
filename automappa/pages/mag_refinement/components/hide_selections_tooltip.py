#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import html
import dash_bootstrap_components as dbc
from automappa.components import ids


# Tooltip for info on store selections behavior
def render() -> html.Div:
    return html.Div(
        dbc.Tooltip(
            'Toggling this to the "on" state will hide your manually-curated MAG refinement groups',
            target=ids.HIDE_SELECTIONS_TOGGLE,
            placement="auto",
        )
    )
