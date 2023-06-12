#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import html, dcc
from automappa.components import ids


def render() -> html.Div:
    return html.Div(
        [
            html.Label("Distribute taxa by rank:"),
            dcc.Dropdown(
                id=ids.TAXONOMY_DISTRIBUTION_DROPDOWN,
                options=[
                    {"label": "Class", "value": "class"},
                    {"label": "Order", "value": "order"},
                    {"label": "Family", "value": "family"},
                    {"label": "Genus", "value": "genus"},
                    {"label": "Species", "value": "species"},
                ],
                value=ids.TAXONOMY_DISTRIBUTION_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
