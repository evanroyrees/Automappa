import dash
import dash_bootstrap_components.themes as dbct
import flask

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbct.SANDSTONE])
app.config.suppress_callback_exceptions = True
