#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash_daq import daq

from automappa.components import ids


# Scatterplot 3D Legend Toggle
scatterplot_3d_legend_toggle = daq.ToggleSwitch(
    id=ids.SCATTERPLOT_3D_LEGEND_TOGGLE,
    value=ids.SCATTERPLOT_2D_LEGEND_TOGGLE_VALUE_DEFAULT,
    size=40,
    color="#c5040d",
    label="Legend",
    labelPosition="top",
    vertical=False,
)
