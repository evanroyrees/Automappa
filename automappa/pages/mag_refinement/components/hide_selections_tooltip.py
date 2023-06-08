#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc
from automappa.components import ids

# Tooltip for info on store selections behavior
hide_selections_tooltip = dbc.Tooltip(
    'Toggling this to the "on" state will hide your manually-curated MAG refinement groups',
    target=ids.HIDE_SELECTIONS_TOGGLE,
    placement="auto",
)
