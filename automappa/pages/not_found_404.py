import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashBlueprint, html


alert = dbc.Alert(
    [
        html.H4("Uh oh!", className="alert-heading"),
        html.P(
            "Looks like you've hit a broken link. Try returning home to continue..."
        ),
        html.Hr(),
        dbc.Button(
            "home", href="/", color="info", class_name="d-flex align-items-center"
        ),
    ],
    color="info",
)


def render() -> DashBlueprint:
    app = DashBlueprint()
    # app.name = ids.NOT_FOUND_404_TAB_ID
    app.name = "not_found_404"
    app.description = "Automappa app link not found 404 page"
    app.title = "<(^^<) Automappa ^(^^)^ 404 (>^^)>"
    app.layout = dbc.Container(
        [
            dbc.Row(
                dbc.Col(html.H1("Automappa 404"), align="center"),
                justify="center",
            ),
            dbc.Row(
                dbc.Col(
                    alert,
                    align="center",
                ),
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(html.H1("<(^^<) ^(^^)^ (>^^)>"), align="center"),
                    dbc.Col(html.H1("<(^^<) ^(^^)^ (>^^)>"), align="center"),
                    dbc.Col(html.H1("<(^^<) ^(^^)^ (>^^)>"), align="center"),
                ],
                justify="center",
            ),
        ],
        fluid=True,
    )
    return app
