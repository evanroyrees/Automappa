from typing import Union
import dash_mantine_components as dmc
from dash_extensions.enrich import DashBlueprint, html
from dash_iconify import DashIconify


def get_icon(
    icon: str, height: int = 30, width: Union[int, None] = None
) -> DashIconify:
    return DashIconify(icon=icon, height=height, width=width)


alert = dmc.Alert(
    dmc.Stack(
        [
            dmc.Text(
                "Uh oh! Looks like you've hit a broken link. Try returning home to continue...",
                size="xl",
                color="gray",
            ),
            dmc.Anchor(
                dmc.Button(
                    "Home",
                    variant="outline",
                    leftIcon=get_icon("line-md:home"),
                    color="info",
                    fullWidth=True,
                ),
                href="/",
                underline=False,
            ),
        ],
        style={"height": 100},
        spacing="xs",
        align="stretch",
        justify="space-around",
    ),
    title="Something went wrong",
    color="info",
)

evan_rees_hover_card = dmc.HoverCard(
    shadow="md",
    children=[
        dmc.HoverCardTarget(
            dmc.Avatar(
                src="https://avatars.githubusercontent.com/u/25933122?v=4",
                radius="xl",
                size="xl",
            )
        ),
        dmc.HoverCardDropdown(
            [
                dmc.Text("Evan Rees", align="center"),
                dmc.Group(
                    [
                        dmc.Anchor(
                            get_icon(icon="openmoji:github", width=40),
                            href="https://www.github.com/WiscEvan/",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            get_icon(icon="openmoji:linkedin", width=40),
                            href="https://www.linkedin.com/in/evanroyrees/",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            get_icon(icon="academicons:google-scholar", width=40),
                            href="https://scholar.google.com/citations?user=9TL02VUAAAAJ",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            get_icon(icon="ic:round-self-improvement", width=40),
                            href="https://wiscevan.github.io",
                            target="_blank",
                        ),
                    ],
                    p=0,
                ),
                dmc.Text("Say hi!", color="dimmed", align="center"),
            ]
        ),
    ],
)
kwanlab_hover_card = dmc.HoverCard(
    shadow="md",
    children=[
        dmc.HoverCardTarget(
            dmc.Avatar(
                src="https://avatars.githubusercontent.com/u/6548561?v=4",
                radius="xl",
                size="xl",
            )
        ),
        dmc.HoverCardDropdown(
            [
                dmc.Text("Jason C. Kwan Lab", align="center"),
                dmc.Group(
                    [
                        dmc.Anchor(
                            get_icon(icon="openmoji:github", width=40),
                            href="https://www.github.com/KwanLab/",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            get_icon(icon="openmoji:linkedin", width=40),
                            href="https://www.linkedin.com/in/jason-kwan-79137324/",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            get_icon(icon="academicons:google-scholar", width=40),
                            href="https://scholar.google.com/citations?user=zKnYsSsAAAAJ",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            get_icon(icon="openmoji:twitter", width=40),
                            href="https://twitter.com/kwan_lab",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            get_icon(icon="guidance:medical-laboratory", width=40),
                            href="https://kwanlab.github.io/",
                            target="_blank",
                        ),
                    ],
                    p=0,
                ),
            ]
        ),
    ],
)


sample_icons = [
    get_icon("file-icons:influxdata"),
    get_icon("healthicons:animal-spider-outline"),
    get_icon("ph:plant"),
    get_icon("healthicons:animal-chicken-outline"),
    get_icon("healthicons:bacteria-outline"),
    get_icon("game-icons:mushrooms-cluster"),
    get_icon("healthicons:malaria-mixed-microscope-outline"),
    get_icon("game-icons:scarab-beetle"),
    get_icon("healthicons:animal-cow-outline"),
    get_icon("fluent-emoji-high-contrast:fish"),
    get_icon("streamline:nature-ecology-potted-cactus-tree-plant-succulent-pot"),
]

new_issue_avatar = html.A(
    dmc.Tooltip(
        dmc.Avatar(
            get_icon("emojione:waving-hand-medium-light-skin-tone"),
            size="md",
            radius="xl",
        ),
        label="Provide feedback",
        position="bottom",
    ),
    href="https://github.com/WiscEvan/Automappa/issues/new",
    target="_blank",
)


def render() -> DashBlueprint:
    app = DashBlueprint()
    app.name = "not_found_404"
    app.description = "Automappa app link not found 404 page"
    app.title = "Automappa 404"
    app.layout = dmc.Container(
        [
            dmc.Space(h=30),
            dmc.Center(alert),
            dmc.Center(
                [
                    new_issue_avatar,
                    dmc.Space(w=30),
                    evan_rees_hover_card,
                    dmc.Space(w=30),
                    kwanlab_hover_card,
                ],
                style={"width": "100%", "height": 200},
            ),
            dmc.Footer(
                dmc.Grid(
                    children=[dmc.Col(icon, span="auto") for icon in sample_icons],
                    justify="space-between",
                    align="center",
                    gutter="xs",
                    grow=True,
                ),
                height=40,
                fixed=True,
                withBorder=False,
            ),
        ],
        fluid=True,
    )
    return app
