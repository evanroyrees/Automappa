#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash_daq as daq

from automappa.components import ids


# Scatterplot 2D Legend Toggle
scatterplot_2d_legend_toggle = daq.ToggleSwitch(
    id=ids.SCATTERPLOT_2D_LEGEND_TOGGLE,
    value=ids.SCATTERPLOT_2D_LEGEND_TOGGLE_VALUE_DEFAULT,
    size=40,
    color="#c5040d",
    label="Legend",
    labelPosition="top",
    vertical=False,
)
