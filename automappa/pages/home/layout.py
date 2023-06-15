import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashBlueprint
from automappa.components import ids
from automappa.pages.home.components import (
    binning_select,
    markers_select,
    metagenome_select,
    cytoscape_connections_select,
    selected_tables_datatable,
    tasks_table,
    upload_modal_button,
    samples_datatable,
    refine_mags_button,
)


def render() -> DashBlueprint:
    app = DashBlueprint()
    app.name = ids.HOME_TAB_ID
    app.icon = "line-md:home"
    app.description = "Automappa home page to upload genome binning results."
    app.title = "Automappa home"
    app.layout = dbc.Container(
        children=[
            dbc.Row(
                [
                    dbc.Col(upload_modal_button.render(app), align="center"),
                    dbc.Col(refine_mags_button.render(app), align="center"),
                ],
                justify="evenly",
            ),
            dbc.Row(dbc.Col(samples_datatable.render(app)), justify="center"),
            dbc.Row(
                [
                    dbc.Col(binning_select.render(app)),
                    dbc.Col(markers_select.render(app)),
                    dbc.Col(metagenome_select.render(app)),
                    dbc.Col(cytoscape_connections_select.render(app)),
                ],
                justify="center",
            ),
            dbc.Row(dbc.Col(selected_tables_datatable.render(app)), justify="center"),
            dbc.Row(dbc.Col(tasks_table.render(app)), justify="center"),
        ],
        fluid=True,
    )
    return app
