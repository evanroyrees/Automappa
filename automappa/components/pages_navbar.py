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
    brand = dmc.Group(
        dmc.Anchor(
            [logo, "  Automappa"],
            href="https://github.com/WiscEvan/Automappa",
            underline=False,
            color="dark",
            size="xl",
            transform="capitalize",
            weight=600,
        ),
        spacing="xl",
        position="center",
        style={"textAlign": "center"},
    )
    link_group = dmc.Group(
        [
            dmc.NavLink(
                label=page["name"],
                href=page["path"],
                icon=DashIconify(icon=page["icon"], height=30),
                variant="subtle",
                color="gray",
                id=page["name"],
                style={"textAlign": "center"},
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
            justify="center",
            align="center",
            gutter="xs",
        ),
        height=50,
        style={"backgroundColor": "#adb5bd"},
        zIndex=99999999,
    )
    return html.Div(header)
