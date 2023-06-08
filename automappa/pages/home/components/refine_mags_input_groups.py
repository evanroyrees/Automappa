# -*- coding: utf-8 -*-

from dash_extensions.enrich import html
import dash_bootstrap_components as dbc

from automappa.pages.home.components import (
    binning_select,
    markers_select,
    metagenome_select,
)


def render(app) -> html.Div:
    return html.Div(
        [
            dbc.InputGroup([dbc.InputGroupText("Binning"), binning_select.render(app)]),
            dbc.InputGroup([dbc.InputGroupText("Markers"), markers_select.render(app)]),
            dbc.InputGroup(
                [dbc.InputGroupText("Metagenome"), metagenome_select.render(app)]
            ),
        ]
    )
