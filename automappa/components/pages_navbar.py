import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash
from dash_extensions.enrich import html


def render() -> html.Div:
    # @app.callback(
    #     Output(ids.PAGES_NAVBAR, "children"),
    # )
    # def update_disabled_navlinks():
    #     ...

    logo = html.Img(src=dash.get_asset_url("favicon.ico"), height="30px")
    brand = dmc.Anchor(
        [logo, "  Automappa"],
        href="https://github.com/WiscEvan/Automappa",
        target="_blank",
        underline=False,
        color="dark",
        size="md",
        transform="capitalize",
        weight=550,
    )
    link_group = dmc.Group(
        [
            dmc.NavLink(
                label=dmc.Text(page["name"], align="center", weight=500),
                href=page["path"],
                icon=DashIconify(icon=page["icon"], height=25),
                variant="subtle",
                color="gray",
                id=page["name"],
            )
            for page in dash.page_registry.values()
            if page["module"] != "not_found_404"
        ],
        position="apart",
        grow=True,
        spacing="xs",
    )

    header = dmc.Header(
        dmc.Grid(
            children=[
                dmc.Col(brand, span=2, style={"textAlign": "center"}),
                dmc.Col(link_group, span=10),
            ],
            justify="space-around",
            align="center",
            gutter="xl",
        ),
        height=55,
        style={"backgroundColor": "#FFFFFF"},
        zIndex=99999999,
    )
    return html.Div(header)
