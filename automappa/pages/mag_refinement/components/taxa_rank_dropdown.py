#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Protocol
from dash_extensions.enrich import html, dcc, DashProxy
from automappa.components import ids


class TaxonomyDistributionDropdownDataSource(Protocol):
    def get_taxonomy_distribution_dropdown_options(
        self,
    ) -> List[Dict[Literal["label", "value"], str]]:
        ...


def render(app: DashProxy, source: TaxonomyDistributionDropdownDataSource) -> html.Div:
    options = source.get_taxonomy_distribution_dropdown_options()
    return html.Div(
        [
            html.Label("Distribute taxa by rank:"),
            dcc.Dropdown(
                id=ids.TAXONOMY_DISTRIBUTION_DROPDOWN,
                options=options,
                value=ids.TAXONOMY_DISTRIBUTION_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
