import dash_bootstrap_components as dbc
import dash
from dash_extensions.enrich import html, DashProxy, Output, Input

from automappa.components import ids


def render() -> html.Div:
    # @app.callback(
    #     Output(ids.PAGES_NAVBAR, "children"),
    # )
    # def update_disabled_navlinks():
    #     ...

    logo = html.Img(src=dash.get_asset_url("favicon.ico"), height="30px")
    brand = dbc.NavbarBrand(
        "Automappa",
        href="https://github.com/WiscEvan/Automappa",
        external_link=True,
    )
    logo_bar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(logo),
                            dbc.Col(brand),
                        ],
                        align="center",
                        justify="start",
                    ),
                    href="https://github.com/WiscEvan/Automappa",
                    style={"textDecoration": "none"},
                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
    )
    nav = dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink(page["name"], href=page["path"]))
            for page in dash.page_registry.values()
            if page["module"] != "not_found_404"
        ],
        fill=True,
        pills=True,
        horizontal=True,
        justified=True,
    )
    return html.Div([logo_bar, dbc.Row(dbc.Col(nav), justify="evenly")])
