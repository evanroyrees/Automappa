import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashBlueprint, html
from dash_iconify import DashIconify


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
    app.name = "not_found_404"
    app.description = "Automappa app link not found 404 page"
    app.title = "Automappa 404"
    app.layout = dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    alert,
                    align="center",
                ),
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [DashIconify(icon="file-icons:influxdata", height=30)],
                        align="center",
                    ),
                    dbc.Col(
                        [
                            DashIconify(
                                icon="healthicons:animal-spider-outline", height=30
                            )
                        ],
                        align="center",
                    ),
                    dbc.Col(
                        [DashIconify(icon="ph:plant", height=30)],
                        align="center",
                    ),
                    dbc.Col(
                        [
                            DashIconify(
                                icon="healthicons:animal-chicken-outline", height=30
                            )
                        ],
                        align="center",
                    ),
                    dbc.Col(
                        [DashIconify(icon="healthicons:bacteria-outline", height=30)],
                        align="center",
                    ),
                    dbc.Col(
                        [DashIconify(icon="game-icons:mushrooms-cluster", height=30)],
                        align="center",
                    ),
                    dbc.Col(
                        [
                            DashIconify(
                                icon="healthicons:malaria-mixed-microscope-outline",
                                height=30,
                            )
                        ],
                        align="center",
                    ),
                    dbc.Col(
                        [DashIconify(icon="game-icons:scarab-beetle", height=30)],
                        align="center",
                    ),
                    dbc.Col(
                        [DashIconify(icon="healthicons:animal-cow-outline", height=30)],
                        align="center",
                    ),
                    dbc.Col(
                        [
                            DashIconify(
                                icon="fluent-emoji-high-contrast:fish", height=30
                            )
                        ],
                        align="center",
                    ),
                    dbc.Col(
                        [
                            DashIconify(
                                icon="streamline:nature-ecology-potted-cactus-tree-plant-succulent-pot",
                                height=30,
                            )
                        ],
                        align="center",
                    ),
                ],
                justify="evenly",
            ),
        ],
        fluid=True,
    )
    return app
