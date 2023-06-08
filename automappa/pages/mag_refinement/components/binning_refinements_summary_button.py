#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc
from automappa.components import ids


# Summarize Refinements Button
binning_refinements_summary_button = [
    dbc.Button(
        "Summarize Refinements",
        id=ids.REFINEMENTS_SUMMARY_BUTTON,
        n_clicks=0,
        color="primary",
    ),
]
