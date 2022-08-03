import dash_bootstrap_components as dbc
import dash_uploader as du

from dash_extensions.enrich import DashProxy
from flask_caching import Cache
from automappa.settings import server,celery
# from automappa.tasks import long_callback_manager

app = DashProxy(
    name=__name__,
    title="Automappa",
    external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP],
    update_title="Automapping...",
    suppress_callback_exceptions=True,
    # long_callback_manager=long_callback_manager,
)
cache = Cache(app.server, config={
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': celery.backend_url
})
du.configure_upload(app=app, folder=server.root_upload_folder)
