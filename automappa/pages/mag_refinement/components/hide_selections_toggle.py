#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash_daq as daq

from automappa.components import ids

# add hide selection toggle
hide_selections_toggle = daq.ToggleSwitch(
    id=ids.HIDE_SELECTIONS_TOGGLE,
    size=40,
    color="#c5040d",
    label="Hide MAG Refinements",
    labelPosition="top",
    vertical=False,
    value=False,
)
