#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dash_extensions.enrich import DashBlueprint
import dash_bootstrap_components as dbc
from automappa.components import ids
from automappa.pages.mag_refinement.components import (
    settings_banner,
    scatterplot_2d,
    mag_metrics_table,
    taxonomy_distribution,
    scatterplot_3d,
    refinements_table,
    mag_refinement_coverage_boxplot,
    mag_refinement_gc_content_boxplot,
    mag_refinement_length_boxplot,
)


def render() -> DashBlueprint:
    app = DashBlueprint()
    app.name = ids.MAG_REFINEMENT_TAB_ID
    app.description = (
        "Automappa MAG refinement page to manually inspect genome binning results."
    )
    app.title = "Automappa MAG refinement"
    app.layout = dbc.Container(
        children=[
            dbc.Row([dbc.Col(settings_banner.render(app))]),
            dbc.Row(
                [
                    dbc.Col(scatterplot_2d.render(app), width=9),
                    dbc.Col(mag_metrics_table.render(app), width=3),
                ]
            ),
            # TODO: Add MAG assembly metrics table
            dbc.Row(
                [
                    dbc.Col(taxonomy_distribution.render(app), width=7),
                    dbc.Col(scatterplot_3d.render(app), width=5),
                    # TODO: dbc.Col(coverage_range_slider.render(app), width=3),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(mag_refinement_coverage_boxplot.render(app), width=4),
                    dbc.Col(mag_refinement_gc_content_boxplot.render(app), width=4),
                    dbc.Col(mag_refinement_length_boxplot.render(app), width=4),
                ]
            ),
            dbc.Row([dbc.Col(refinements_table.render(app), width=12)]),
        ],
        fluid=True,
    )
    return app
