#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import dcc, html
from automappa.components import ids


def render() -> html.Div:
    return html.Div(
        [
            html.Label("K-mer size:"),
            dcc.Dropdown(
                id=ids.KMER_SIZE_DROPDOWN,
                options=[3, 4, 5],
                value=ids.KMER_SIZE_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
