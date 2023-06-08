import dash_bootstrap_components as dbc
import dash_uploader as du

from dash_extensions.enrich import DashProxy, ServersideOutputTransform
from automappa import settings

app = DashProxy(
    name=__name__,
    title="Automappa",
    external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP],
    update_title="Automapping...",
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=False,
    use_pages=True,
    pages_folder="",
    transforms=[ServersideOutputTransform()],
)

# Setup main app layout.
du.configure_upload(app=app, folder=settings.server.root_upload_folder)
