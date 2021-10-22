import dash
import dash_bootstrap_components.themes as dbct

app = dash.Dash(__name__, external_stylesheets=[dbct.LUX])
app.config.suppress_callback_exceptions = True
