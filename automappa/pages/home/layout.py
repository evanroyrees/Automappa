import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashBlueprint, html
from automappa.components import ids
from automappa.pages.home.components import (
    refine_mags_input_groups,
    selected_tables_datatable,
    tasks_table,
    upload_modal,
    samples_datatable,
    refine_mags_button,
)


def render() -> DashBlueprint:
    app = DashBlueprint()
    app.name = ids.HOME_TAB_ID
    app.description = "Automappa home page to upload genome binning results."
    app.title = "Automappa home"
    app.layout = dbc.Container(
        children=[
            dbc.Row(
                [
                    dbc.Col(upload_modal.render(app), width=2, align="center"),
                    dbc.Col(refine_mags_button.render(app), width=2, align="center"),
                ],
                justify="center",
            ),
            dbc.Row(dbc.Col(samples_datatable.render(app)), justify="center"),
            dbc.Row(
                dbc.Col(refine_mags_input_groups.render(app), width=12, align="center"),
                justify="center",
            ),
            dbc.Row(dbc.Col(selected_tables_datatable.render(app)), justify="center"),
            dbc.Row(dbc.Col(tasks_table.render(app)), justify="center"),
        ],
        fluid=True,
    )
    return app
