
import dash
import dash_bootstrap_components as dbc
import dash_uploader as du

from automappa.settings import server

app = dash.Dash(
    name=__name__,
    title="Automappa",
    external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP],
    update_title="Automapping...",
    suppress_callback_exceptions=True,
)

du.configure_upload(app=app, folder=server.root_upload_folder)
