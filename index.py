#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from app import app
from apps import explorer, summary

tab_style = {
    "borderTop": "3px solid white",
    "borderBottom": "0px",
    "borderLeft": "0px",
    "borderRight": "0px",
    "backgroundColor": "#9b0000",
}

tab_selected_style = {
    "borderTop": "3px solid #c5040d",
    "borderBottom": "0px",
    "borderLeft": "0px",
    "borderRight": "0px",
    "fontWeight": "bold",
    "color": "white",
    "backgroundColor": "#c5040d",
}


def layout(df, cluster_columns):
    app.layout = html.Div(
        [
            # Hidden div that saves dataframe for each tab
            html.Div(
                df.to_json(orient="split"), id="binning_df", style={"display": "none"}
            ),
            html.Div(
                df[cluster_columns].to_json(orient="split"),
                id="refinement-data",
                style={"display": "none"},
            ),
            html.Link(
                href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",
                rel="stylesheet",
            ),
            html.Link(
                href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"
            ),
            html.Link(
                href="https://fonts.googleapis.com/css?family=Open+Sans",
                rel="stylesheet",
            ),
            html.Link(
                href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"
            ),
            html.Link(href="static/dash_crm.css", rel="stylesheet"),
            html.Link(href="static/stylesheet.css", rel="stylesheet"),
            # header
            html.Div(
                [
                    html.Label(
                        "Autometa Dashboard", className="three columns app-title"
                    ),
                    html.Div(
                        [
                            dcc.Tabs(
                                id="tabs",
                                style={"height": "10", "verticalAlign": "middle"},
                                children=[
                                    dcc.Tab(
                                        label="Bin Exploration",
                                        value="explorer_tab",
                                        style=tab_style,
                                        selected_style=tab_selected_style,
                                    ),
                                    dcc.Tab(
                                        id="bin_summary",
                                        label="Binning Summary",
                                        value="summary_tab",
                                        style=tab_style,
                                        selected_style=tab_selected_style,
                                    ),
                                ],
                                value="explorer_tab",
                            ),
                        ],
                        className="seven columns row header",
                    ),
                    html.Div(
                        html.Img(src="static/UWlogo.png", height="100%"),
                        style={"float": "right", "height": "100%"},
                        className="two columns",
                    ),
                ],
                className="row header",
            ),
            # Tab content
            html.Div(id="tab_content", className="row", style={"margin": "0.5% 0.5%"}),
        ],
        className="row",
        style={"margin": "0%"},
    )


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "explorer_tab":
        return explorer.layout
    elif tab == "summary_tab":
        return summary.layout
    else:
        return explorer.layout


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="ML_recruitment.tab or recursive_dbscan.tab.",
        required=True,
    )
    parser.add_argument(
        "--port",
        help="port to expose",
        default="8050",
    )
    parser.add_argument(
        "--host",
        help="host ip address to expose",
        default="0.0.0.0",
    )
    parser.add_argument(
        "--production",
        help="take autometa-app out of debug mode",
        action="store_false",
        default=True,
    )
    args = parser.parse_args()
    try:
        PORT = int(args.port)
    except ValueError as err:
        print("Must specify an integer for port!")
        print(f"{args.port} is not an integer")
        exit(1)
    df = pd.read_csv(args.input, sep="\t")
    cols = [
        col
        for col in df.columns
        if "refinement_" in col or "cluster" in col or "contig" in col
    ]
    layout(df, cluster_columns=cols)
    app.run_server(host=args.host, port=PORT, debug=args.production)
