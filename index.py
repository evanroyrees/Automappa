#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pandas as pd

from dash.dependencies import Input, Output
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

from autometa.common.markers import load as load_markers

from apps import mag_refinement, mag_summary
from app import app


@app.callback(Output("tab_content", "children"), [Input("tabs", "active_tab")])
def render_content(active_tab):
    if active_tab == "mag_refinement":
        return mag_refinement.layout
    elif active_tab == "mag_summary":
        return mag_summary.layout
    else:
        return active_tab


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Automappa: An interactive interface for exploration of metagenomes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--binning-main",
        help="Path to --binning-main output of Autometa binning/recruitment results",
        type=str,
        metavar="filepath",
        required=True,
    )
    parser.add_argument(
        "--markers",
        help="Path to Autometa-formatted markers table (may be taxon-specific)",
        type=str,
        metavar="filepath",
        required=True,
    )
    parser.add_argument(
        "--fasta",
        help="Path to metagenome.fasta",
        type=str,
        metavar="filepath",
        required=False,
    )
    parser.add_argument(
        "--port", help="port to expose", default=8050, type=int, metavar="number"
    )
    parser.add_argument(
        "--host",
        help="host ip address to expose",
        type=str,
        default="0.0.0.0",
        metavar="ip address",
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
    markers = load_markers(args.markers).reset_index().copy()

    # binning and taxonomy are added here to color contigs
    # NOTE: (Optional) parameter of fasta in case the user would like to
    # export the MAG refinements as a fasta file

    print(f"binning shape:\t\t{binning.shape}")
    print(f"markers shape:\t\t{markers.shape}")
    print(
        "Data loaded. It may take a minute or two to construct all interactive graphs..."
    )

    # NOTE: MAG refinement columns are enumerated (1-indexed) and prepended with 'refinement_'
    binning_cols = [
        col
        for col in binning.columns
        if "refinement_" in col or "cluster" in col or "contig" in col
    ]

    refinement_tab = dbc.Tab(label="MAG Refinement", tab_id="mag_refinement")
    summary_tab = dbc.Tab(label="MAG Summary", tab_id="mag_summary")

    app.layout = dbc.Container(
        [
            # hidden divs
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
            html.Title("Automappa"),
            # Navbar
            dbc.Tabs(
                id="tabs", children=[refinement_tab, summary_tab], className="nav-fill"
            ),
            html.Div(id="tab_content"),
        ],
        fluid=True,
    )

    app.run_server(host=args.host, port=args.port, debug=args.debug)
