import dash_mantine_components as dmc

from dash_iconify import DashIconify

from dash_extensions.enrich import DashProxy, html
from automappa.components import ids
from automappa.pages.mag_refinement.components import settings_offcanvas


def render(app: DashProxy) -> html.Div:
    return html.Div(
        [
            dmc.Button(
                "Settings",
                id=ids.SETTINGS_BUTTON,
                n_clicks=0,
                size="md",
                leftIcon=[DashIconify(icon="clarity:settings-line")],
                variant="gradient",
                gradient={"from": "#CA2270", "to": "#F36E2D"},
                fullWidth=True,
            ),
            settings_offcanvas.render(app),
        ]
    )
