#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import plotly.plotly as py
from plotly import graph_objs as go
import math
import sys
from app import app, server
from apps import explorer, summary


usage = 'index.py </path/to/autometa.binning.tsv>'
# '</path/to/cluster_taxonomy.tsv> </path/to/cluster_summary.tsv>'
if not len(sys.argv) >= 2:
    sys.exit(usage)

bin_fpath = sys.argv[1]
df = pd.read_csv(bin_fpath, sep='\t')

app.layout = html.Div(
    [
        # header
        html.Div([

            html.Span("Autometa Dashboard", className='app-title'),

            html.Div(
                html.Img(src='static/UWlogo.png', height="100%")
                ,style={"float":"right","height":"100%"})
            ],
            className="row header"
            ),

        # tabs
        html.Div([

            dcc.Tabs(
                id="tabs",
                style={"height":"20","verticalAlign":"middle"},
                children=[
                    dcc.Tab(label="Projects", value="projects_tab"),
                    dcc.Tab(label="Bin Exploration", value="explorer_tab"),
                    dcc.Tab(id="bin_summary", label="Binning Summary", value="summary_tab"),
                ],
                value="explorer_tab",
            )

            ],
            className="row tabs_div"
            ),

        # divs that save dataframe for each tab
        # html.Div(wq_manager.get_projects().to_json(orient="split"), id="projects_df", style={"display": "none"}), # projects df
        html.Div(df.to_json(orient='split'), id="binning_df", style={"display": "none"}), # leads df

        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),

        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(href="static/dash_crm.css", rel="stylesheet")
    ],
    className="row",
    style={"margin": "0%"},
)


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "projects_tab":
        return explorer.layout
        # return opportunities.layout
    elif tab == "explorer_tab":
        return explorer.layout
    elif tab == "summary_tab":
        return summary.layout
        # return cases.layout
    else:
        return explorer.layout
        # return opportunities.layout

if __name__ == "__main__":
    app.run_server(debug=True)
