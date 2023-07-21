#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_extensions.enrich import html
import dash_mantine_components as dmc
from automappa.components import ids


# Summarize Refinements Button
def render() -> html.Div:
    return html.Div(
        dmc.Button(
            "Summarize Refinements",
            id=ids.REFINEMENTS_SUMMARY_BUTTON,
            n_clicks=0,
            color="dark",
            fullWidth=True,
        ),
        # TODO: Create background task to compute binning summary metrics
        # TODO: Create downloader task to download file of computed summary metrics
    )
