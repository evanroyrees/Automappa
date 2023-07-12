import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashBlueprint
from automappa.components import ids
from automappa.pages.mag_summary.source import SummaryDataSource
from automappa.pages.mag_summary.components import (
    mag_coverage_boxplot,
    mag_gc_content_boxplot,
    mag_length_boxplot,
    mag_overview_coverage_boxplot,
    mag_overview_length_boxplot,
    mag_overview_gc_content_boxplot,
    mag_overview_metrics_boxplot,
    mag_selection_dropdown,
    mag_summary_stats_datatable,
    mag_taxonomy_sankey,
    mag_metrics_barplot,
)


def render(source: SummaryDataSource) -> DashBlueprint:
    app = DashBlueprint()
    app.name = ids.MAG_SUMMARY_TAB_ID
    app.icon = "material-symbols:auto-graph-rounded"
    app.description = (
        "Automappa MAG summary page displaying overview of genome binning results."
    )
    app.title = "Automappa MAG summary"

    app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(mag_overview_metrics_boxplot.render(app, source), width=3),
                    dbc.Col(
                        mag_overview_gc_content_boxplot.render(app, source), width=3
                    ),
                    dbc.Col(mag_overview_length_boxplot.render(app, source), width=3),
                    dbc.Col(mag_overview_coverage_boxplot.render(app, source), width=3),
                ]
            ),
            dbc.Row(dbc.Col(mag_summary_stats_datatable.render(app, source))),
            dbc.Row(dbc.Col(mag_selection_dropdown.render(app, source))),
            dbc.Row(dbc.Col(mag_taxonomy_sankey.render(app, source))),
            dbc.Row(
                [
                    dbc.Col(mag_metrics_barplot.render(app, source), width=3),
                    dbc.Col(mag_gc_content_boxplot.render(app, source), width=3),
                    dbc.Col(mag_length_boxplot.render(app, source), width=3),
                    dbc.Col(mag_coverage_boxplot.render(app, source), width=3),
                ]
            ),
        ],
        fluid=True,
    )

    return app
