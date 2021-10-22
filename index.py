#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pandas as pd

from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from apps import mag_refinement, mag_summary, functions
from app import app


def layout(
    binning: pd.DataFrame,
    markers: pd.DataFrame,
):
    # NOTE: MAG refinement columns are enumerated (1-indexed) and prepended with 'refinement_'
    binning_cols = [
        col
        for col in binning.columns
        if "refinement_" in col or "cluster" in col or "contig" in col
    ]

    navbar = dbc.NavbarSimple(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(src="static/UWlogo.png", height="30px"),
                        width="auto",
                    ),
                ],
                align="center",
                className="g-0",
                justify="end",
            ),
        ],
        brand="Automappa",
        color="#c5050c",
        dark=True,
    )
    app.layout = dbc.Container(
        [
            # hidden divs
            html.Div(
                binning.to_json(orient="split"),
                id="binning_df",
                style={"display": "none"},
            ),
            html.Div(
                markers.to_json(orient="split"),
                id="kingdom-markers",
                style={"display": "none"},
            ),
            html.Div(
                binning.to_json(orient="split"),
                id="metagenome-annotations",
                style={"display": "none"},
            ),
            html.Div(
                binning[binning_cols].to_json(orient="split"),
                id="refinement-data",
                style={"display": "none"},
            ),
            navbar,
            dcc.Tabs(
                id="tabs",
                # style={"height": "10", "verticalAlign": "middle"},
                children=[
                    dcc.Tab(
                        label="MAG Refinement",
                        value="mag_refinement",
                        # style=tab_style,
                        # selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        id="mag_summary",
                        label="MAG Summary",
                        value="mag_summary",
                        # style=tab_style,
                        # selected_style=tab_selected_style,
                    ),
                ],
                value="mag_refinement",
            ),
            html.Div(id="tab_content"),
        ],
        fluid=True,
    )
    # app.layout = html.Div(
    #     [
    #         #### Send data to hidden divs for use in explorer.py and summary.py
    #         html.Div(
    #             binning.to_json(orient="split"),
    #             id="binning_df",
    #             style={"display": "none"},
    #         ),
    #         html.Div(
    #             markers.to_json(orient="split"),
    #             id="kingdom-markers",
    #             style={"display": "none"},
    #         ),
    #         html.Div(
    #             binning.to_json(orient="split"),
    #             id="metagenome-annotations",
    #             style={"display": "none"},
    #         ),
    #         html.Div(
    #             binning[binning_cols].to_json(orient="split"),
    #             id="refinement-data",
    #             style={"display": "none"},
    #         ),
    #         #### Navbar div with Automappa tabs and School Logo
    #         html.Div(
    #             [
    #                 # html.Label(
    #                 #     "Automappa Dashboard", className="three columns app-title"
    #                 # ),
    #                 html.Div(
    #                     [
    #                         dcc.Tabs(
    #                             id="tabs",
    #                             # style={"height": "10", "verticalAlign": "middle"},
    #                             children=[
    #                                 dcc.Tab(
    #                                     label="MAG Refinement",
    #                                     value="mag_refinement",
    #                                     # style=tab_style,
    #                                     # selected_style=tab_selected_style,
    #                                 ),
    #                                 dcc.Tab(
    #                                     id="mag_summary",
    #                                     label="MAG Summary",
    #                                     value="mag_summary",
    #                                     # style=tab_style,
    #                                     # selected_style=tab_selected_style,
    #                                 ),
    #                             ],
    #                             value="mag_refinement",
    #                         ),
    #                     ],
    #                     # className="seven columns row header",
    #                 ),
    #                 # html.Div(
    #                 #     html.Img(src="static/UWlogo.png", height="100%"),
    #                 #     style={"float": "right", "height": "100%"},
    #                 # className="two columns",
    #                 # ),
    #             ],
    #             # className="row header",
    #         ),
    #         #### Below Navbar where we render selected tab content
    #         html.Div(
    #             id="tab_content",
    #             # className="row",
    #             # style={"margin": "0.5% 0.5%"}
    #         ),
    #     ],
    #     # className="row",
    #     # style={"margin": "0%"},
    # )


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "mag_refinement":
        return mag_refinement.layout
    elif tab == "mag_summary":
        return mag_summary.layout
    else:
        return mag_refinement.layout


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Automappa: An interactive interface for exploration of metagenomes"
    )
    parser.add_argument(
        "--binning-main",
        help="Path to --binning-main output of Autometa binning/recruitment results",
        required=True,
    )
    parser.add_argument(
        "--markers",
        help="Path to Autometa-formatted markers table (may be taxon-specific)",
        required=False,
    )
    parser.add_argument(
        "--fasta",
        help="Path to metagenome.fasta",
        required=False,
    )
    parser.add_argument("--port", help="port to expose", default=8050, type=int)
    parser.add_argument(
        "--host",
        help="host ip address to expose",
        default="0.0.0.0",
    )
    parser.add_argument(
        "--debug",
        help="Turn on debug mode",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    print("Please wait a moment while all of the data is loaded.")
    # Needed separately for binning refinement selections.
    binning = pd.read_csv(args.binning_main, sep="\t")
    # Needed for completeness/purity calculations
    markers = functions.load_markers(args.markers)

    # binning and taxonomy are added here to color contigs
    # NOTE: (Optional) parameter of fasta in case the user would like to
    # export the MAG refinements as a fasta file

    print(f"binning shape:\t\t{binning.shape}")
    print(f"markers shape:\t\t{markers.shape}")
    print(
        "Data loaded. It may take a minute or two to construct all interactive graphs..."
    )

    layout(binning=binning, markers=markers)

    app.run_server(host=args.host, port=args.port, debug=args.debug)
