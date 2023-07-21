from dash_extensions.enrich import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify


# TODO: Refactor to update scatterplot legend with update marker symbol traces...
def render() -> html.Div:
    return html.Div(
        [
            dbc.Row(
                dbc.Col(dmc.Title("Marker Symbol Count Legend", order=6)),
                justify="start",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dmc.Badge(
                            ": 0",
                            leftSection=[DashIconify(icon="ph:circle-bold")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                    dbc.Col(
                        dmc.Badge(
                            ": 1",
                            leftSection=[DashIconify(icon="uil:square")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                    dbc.Col(
                        dmc.Badge(
                            ": 2",
                            leftSection=[DashIconify(icon="ph:diamond-bold")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                    dbc.Col(
                        dmc.Badge(
                            ": 3",
                            leftSection=[DashIconify(icon="tabler:triangle")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                    dbc.Col(
                        dmc.Badge(
                            ": 4",
                            leftSection=[DashIconify(icon="tabler:x")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                    dbc.Col(
                        dmc.Badge(
                            ": 5",
                            leftSection=[DashIconify(icon="tabler:pentagon")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                    dbc.Col(
                        dmc.Badge(
                            ": 6",
                            leftSection=[DashIconify(icon="tabler:hexagon")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                    dbc.Col(
                        dmc.Badge(
                            ": 7+",
                            leftSection=[DashIconify(icon="mdi:hexagram-outline")],
                            size="lg",
                            radius="xl",
                            color="dark",
                            variant="outline",
                            fullWidth=True,
                        )
                    ),
                ],
                justify="evenly",
            ),
        ]
    )
