# -*- coding: utf-8 -*-

import dash_daq as daq
import dash_bootstrap_components as dbc

from dash_extensions.enrich import DashProxy, Input, Output, State, dcc, html
from automappa.components import ids
from automappa.pages.mag_refinement.components import (
    binning_refinements_download_button,
    color_by_col_dropdown,
)


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

# Summarize Refinements Button
binning_refinements_summary_button = [
    dbc.Button(
        "Summarize Refinements",
        id=ids.REFINEMENTS_SUMMARY_BUTTON,
        n_clicks=0,
        color="primary",
    ),
]

kmer_size_dropdown = [
    html.Label("K-mer size:"),
    dcc.Dropdown(
        id=ids.KMER_SIZE_DROPDOWN,
        options=[3, 4, 5],
        value=ids.KMER_SIZE_DROPDOWN_VALUE_DEFAULT,
        clearable=False,
    ),
]

norm_method_dropdown = [
    html.Label("K-mer norm. method:"),
    dcc.Dropdown(
        id=ids.NORM_METHOD_DROPDOWN,
        options=["am_clr", "ilr"],
        value=ids.NORM_METHOD_DROPDOWN_VALUE_DEFAULT,
        clearable=False,
    ),
]

scatterplot_2d_axes_dropdown = [
    html.Label("Axes:"),
    dcc.Dropdown(
        id=ids.AXES_2D_DROPDOWN,
        value=ids.AXES_2D_DROPDOWN_VALUE_DEFAULT,
        clearable=False,
    ),
]


scatterplot_3d_zaxis_dropdown = [
    html.Label("Z-axis:"),
    dcc.Dropdown(
        id=ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN,
        options=[
            {"label": "Coverage", "value": "coverage"},
            {"label": "GC%", "value": "gc_content"},
            {"label": "Length", "value": "length"},
        ],
        value=ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN_VALUE_DEFAULT,
        clearable=False,
    ),
]

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

taxa_rank_dropdown = [
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


def render(app: DashProxy) -> dbc.Offcanvas:
    @app.callback(
        Output(ids.SETTINGS_OFFCANVAS, "is_open"),
        Input(ids.SETTINGS_BUTTON, "n_clicks"),
        [State(ids.SETTINGS_OFFCANVAS, "is_open")],
    )
    def toggle_offcanvas(n1: int, is_open: bool) -> bool:
        if n1:
            return not is_open
        return is_open

    return dbc.Offcanvas(
        [
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(color_by_col_dropdown.render(app)),
                                    dbc.Col(scatterplot_2d_legend_toggle),
                                ]
                            ),
                            dbc.Row(dbc.Col(kmer_size_dropdown)),
                            dbc.Row(dbc.Col(norm_method_dropdown)),
                            dbc.Row(dbc.Col(scatterplot_2d_axes_dropdown)),
                        ],
                        title="Figure 1: 2D Metagenome Overview",
                    ),
                    dbc.AccordionItem(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(scatterplot_3d_zaxis_dropdown),
                                    dbc.Col(scatterplot_3d_legend_toggle),
                                ]
                            ),
                        ],
                        title="Figure 2: 3D Metagenome Overview",
                    ),
                    dbc.AccordionItem(
                        [
                            dbc.Col(taxa_rank_dropdown),
                        ],
                        title="Figure 3: Taxonomic Distribution",
                    ),
                ],
                start_collapsed=True,
                flush=True,
            ),
            dbc.Row(
                [
                    dbc.Col(binning_refinements_download_button.render(app)),
                    dbc.Col(binning_refinements_summary_button),
                ]
            ),
        ],
        id=ids.SETTINGS_OFFCANVAS,
        title="Settings",
        is_open=False,
        placement="end",
        scrollable=True,
    )
