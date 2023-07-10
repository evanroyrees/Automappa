# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc

from dash_extensions.enrich import DashProxy, Input, Output, State, html
import dash_mantine_components as dmc

from automappa.components import ids
from automappa.pages.mag_refinement.components import (
    binning_refinements_download_button,
    color_by_col_dropdown,
    scatterplot_2d_legend_toggle,
    scatterplot_2d_axes_dropdown,
    # binning_refinements_summary_button,
    kmer_size_dropdown,
    norm_method_dropdown,
    scatterplot_3d_zaxis_dropdown,
    scatterplot_3d_legend_toggle,
    taxa_rank_dropdown,
)


def render(app: DashProxy, source) -> dbc.Offcanvas:
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
                                    dbc.Col(color_by_col_dropdown.render(app, source)),
                                    dbc.Col(scatterplot_2d_legend_toggle.render()),
                                ]
                            ),
                            dbc.Row(dbc.Col(kmer_size_dropdown.render())),
                            dbc.Row(dbc.Col(norm_method_dropdown.render())),
                            dbc.Row(
                                dbc.Col(
                                    scatterplot_2d_axes_dropdown.render(app, source)
                                )
                            ),
                        ],
                        title="Figure 1: 2D Metagenome Overview",
                    ),
                    dbc.AccordionItem(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        scatterplot_3d_zaxis_dropdown.render(
                                            app, source
                                        )
                                    ),
                                    dbc.Col(scatterplot_3d_legend_toggle.render()),
                                ]
                            ),
                        ],
                        title="Figure 2: 3D Metagenome Overview",
                    ),
                    dbc.AccordionItem(
                        [
                            dbc.Col(taxa_rank_dropdown.render(app, source)),
                        ],
                        title="Figure 3: Taxonomic Distribution",
                    ),
                ],
                start_collapsed=True,
                flush=True,
            ),
            html.Br(),
            dmc.Divider(label="Get MAG refinements data", labelPosition="center"),
            html.Br(),
            dbc.Row(
                dbc.Col(
                    binning_refinements_download_button.render(app, source),
                    align="stretch",
                ),
                justify="center",
            ),
        ],
        id=ids.SETTINGS_OFFCANVAS,
        title="Settings",
        is_open=False,
        placement="end",
        scrollable=True,
    )
