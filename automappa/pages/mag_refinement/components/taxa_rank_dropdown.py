#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
import dash_mantine_components as dmc
from dash_extensions.enrich import html, DashProxy
from automappa.components import ids


class TaxonomyDistributionDropdownDataSource(Protocol):
    def get_taxonomy_distribution_dropdown_options(
        self,
    ) -> List[Dict[Literal["label", "value"], str]]:
        ...


def render(app: DashProxy, source: TaxonomyDistributionDropdownDataSource) -> html.Div:
    options = source.get_taxonomy_distribution_dropdown_options()
    radios = [
        dmc.Radio(option["label"], value=option["value"], color="orange")
        for option in options
    ]
    return html.Div(
        [
            html.Label("Distribute taxa by rank:"),
            dmc.RadioGroup(
                radios,
                id=ids.TAXONOMY_DISTRIBUTION_DROPDOWN,
                value=ids.TAXONOMY_DISTRIBUTION_DROPDOWN_VALUE_DEFAULT,
                orientation="vertical",
            ),
        ]
    )
