import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    name=__name__,
    title="Automappa",
    external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP],
    update_title="Automapping...",
)
app.config.suppress_callback_exceptions = True
