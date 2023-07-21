import dash_bootstrap_components as dbc

from dash_extensions.enrich import (
    DashProxy,
    ServersideOutputTransform,
)
import dash_uploader as du
from automappa.data.database import redis_backend, file_system_backend
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
    transforms=[
        ServersideOutputTransform(
            default_backend=[file_system_backend],
            backends=[redis_backend, file_system_backend],
        ),
    ],
)

du.configure_upload(app=app, folder=settings.server.root_upload_folder)
