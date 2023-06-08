# -*- coding: utf-8 -*-

import dash_daq as daq
import dash_bootstrap_components as dbc

from dash_extensions.enrich import DashProxy, html
from automappa.components import ids
from automappa.pages.mag_refinement.components import settings_offcanvas

refinement_settings_button = dbc.Button("Settings", id=ids.SETTINGS_BUTTON, n_clicks=0)

mag_refinement_save_button = dbc.Button(
    "Save selection to MAG refinement",
    id=ids.MAG_REFINEMENTS_SAVE_BUTTON,
    n_clicks=0,
    disabled=True,
)

# Tooltip for info on store selections behavior
hide_selections_tooltip = dbc.Tooltip(
    'Toggling this to the "on" state will hide your manually-curated MAG refinement groups',
    target=ids.HIDE_SELECTIONS_TOGGLE,
    placement="auto",
)

# add hide selection toggle
hide_selections_toggle = daq.ToggleSwitch(
    id=ids.HIDE_SELECTIONS_TOGGLE,
    size=40,
    color="#c5040d",
    label="Hide MAG Refinements",
    labelPosition="top",
    vertical=False,
    value=ids.HIDE_SELECTIONS_TOGGLE_VALUE_DEFAULT,
)

# TODO: Refactor to update scatterplot legend with update marker symbol traces...
marker_symbols_label = html.Pre(
    """
Marker Symbol    Circle: 0    Diamond:  2          X: 4    Hexagon: 6
 Count Legend    Square: 1   Triangle:  3   Pentagon: 5   Hexagram: 7+
"""
)


def render(app: DashProxy) -> html.Div:
    return html.Div(
        [
            refinement_settings_button,
            settings_offcanvas.render(app),
            mag_refinement_save_button,
            hide_selections_toggle,
            hide_selections_tooltip,
            marker_symbols_label,
        ],
        className="d-grid gap-2 d-md-flex justify-content-md-start",
    )
