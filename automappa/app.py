import dash
import dash_bootstrap_components as dbc
import dash_uploader as du

from automappa.settings import server
from automappa.tasks import long_callback_manager

app = dash.Dash(
    name=__name__,
    title="Automappa",
    external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP],
    update_title="Automapping...",
    suppress_callback_exceptions=True,
    long_callback_manager=long_callback_manager,
)

du.configure_upload(app=app, folder=server.root_upload_folder)
