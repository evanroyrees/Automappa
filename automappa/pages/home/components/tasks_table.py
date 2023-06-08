# -*- coding: utf-8 -*-

from dash_extensions.enrich import DashProxy, Input, Output, html
import dash_bootstrap_components as dbc

from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    return html.Div(id="embedding-tasks")
