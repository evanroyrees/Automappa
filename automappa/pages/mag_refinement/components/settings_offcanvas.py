# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc

from dash_extensions.enrich import DashProxy, Input, Output, State
import dash_mantine_components as dmc

from automappa.components import ids
from automappa.pages.mag_refinement.components import (
    binning_refinements_download_button,
    color_by_col_dropdown,
    scatterplot_2d_legend_toggle,
    scatterplot_2d_axes_dropdown,
    binning_refinements_clear_button,
    scatterplot_3d_zaxis_dropdown,
    scatterplot_3d_legend_toggle,
    taxa_rank_dropdown,
)


def render(app: DashProxy, source) -> dbc.Offcanvas:
    @app.callback(
        Output(ids.SETTINGS_OFFCANVAS, "opened"),
        Input(ids.SETTINGS_BUTTON, "n_clicks"),
        [State(ids.SETTINGS_OFFCANVAS, "opened")],
    )
    def toggle_offcanvas(n1: int, opened: bool) -> bool:
        if n1:
            return not opened
        return opened

    return dmc.Drawer(
        [
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        scatterplot_2d_axes_dropdown.render(
                                            app, source
                                        ),
                                        scatterplot_2d_legend_toggle.render(),
                                    ],
                                    spacing="xl",
                                ),
                                color_by_col_dropdown.render(app, source),
                            ]
                        ),
                        title="Figure 1: 2D Metagenome Overview",
                    ),
                    dbc.AccordionItem(
                        dmc.Group(
                            [
                                scatterplot_3d_zaxis_dropdown.render(app, source),
                                scatterplot_3d_legend_toggle.render(),
                            ],
                            position="left",
                            spacing="xl",
                        ),
                        title="Figure 2: 3D Metagenome Overview",
                    ),
                    dbc.AccordionItem(
                        [
                            dmc.Stack(taxa_rank_dropdown.render(app, source)),
                        ],
                        title="Figure 3: Taxonomic Distribution",
                    ),
                ],
                start_collapsed=True,
                flush=True,
            ),
            dmc.Space(h=15),
            dmc.Divider(
                label="Get MAG refinements data",
                labelPosition="center",
            ),
            dmc.Space(h=10),
            dmc.Group(
                [
                    dmc.Space(w=10),
                    binning_refinements_download_button.render(app, source),
                ]
            ),
            dmc.Space(h=15),
            dmc.Divider(
                label=dmc.Text("Danger zone", weight=700),
                labelPosition="center",
                color="red",
                size="md",
            ),
            dmc.Space(h=10),
            dmc.Group(
                [dmc.Space(w=10), binning_refinements_clear_button.render(app, source)]
            ),
        ],
        id=ids.SETTINGS_OFFCANVAS,
        title="Settings",
        opened=False,
        position="right",
        size=420,
    )
