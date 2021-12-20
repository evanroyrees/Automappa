#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import pandas as pd

from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from autometa.common.markers import load as load_markers

from automappa.utils import (
    convert_marker_counts_to_marker_symbols,
    get_contig_marker_counts,
)

from apps import mag_refinement, mag_summary
from app import app


@app.callback(Output("tab-content", "children"), [Input("tabs", "active_tab")])
def render_content(active_tab):
    if active_tab == "mag_refinement":
        return mag_refinement.layout
    elif active_tab == "mag_summary":
        return mag_summary.layout
    else:
        return active_tab


def main():
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

    # Metagenome Annotations Store
    metagenome_annotations_store = dcc.Store(
        id="metagenome-annotations",
        storage_type="session",
        data=binning.to_json(orient="split"),
    )

    # Kingdom Markers Store
    markers_store = dcc.Store(
        id="markers-store",
        storage_type="session",
        data=markers.to_json(orient="split"),
    )

    # MAG Refinement Data Store
    # NOTE: MAG refinement columns are enumerated (1-indexed) and prepended with 'refinement_'
    if "cluster" not in binning.columns:
        binning["cluster"] = "unclustered"
    else:
        binning["cluster"].fillna("unclustered", inplace=True)

    binning_cols = [
        col
        for col in binning.columns
        if "refinement_" in col or "cluster" in col or "contig" in col
    ]

    print(binning[binning_cols].columns)

    refinement_data_store = dcc.Store(
        id="refinement-data",
        storage_type="session",
        data=binning[binning_cols].to_json(orient="split"),
    )

    # Contig Marker Symbols Store
    contig_marker_counts = get_contig_marker_counts(
        binning.set_index("contig"), markers.set_index("contig")
    )
    contig_marker_symbols = convert_marker_counts_to_marker_symbols(
        contig_marker_counts
    ).reset_index()
    contig_marker_symbols.reset_index().to_json(orient="split")
    contig_marker_symbols_store = dcc.Store(
        id="contig-marker-symbols-store",
        storage_type="memory",
        data=contig_marker_symbols.to_json(orient="split"),
    )

    print(f"binning shape:\t\t{binning.shape}")
    print(f"markers shape:\t\t{markers.shape}")
    print(
        "Data loaded. It may take a minute or two to construct all interactive graphs..."
    )

    refinement_tab = dbc.Tab(label="MAG Refinement", tab_id="mag_refinement")
    summary_tab = dbc.Tab(label="MAG Summary", tab_id="mag_summary")

    app.layout = dbc.Container(
        [
            dbc.Col(markers_store),
            dbc.Col(metagenome_annotations_store),
            dbc.Col(refinement_data_store),
            dbc.Col(contig_marker_symbols_store),
            # Navbar
            dbc.Tabs(
                id="tabs", children=[refinement_tab, summary_tab], className="nav-fill"
            ),
            html.Div(id="tab-content"),
        ],
        fluid=True,
    )

    # TODO: Replace cli inputs (as well as updating title once file is uploaded...)
    # dcc.Upload(id='metagenome-annotations-upload', children=dbc.Button("Upload annotations"))
    # dcc.Upload(id='markers-upload', children=dbc.Button("Upload annotations"))
    sample_name = os.path.basename(args.binning_main).replace(" ", "_").split(".")[0]
    app.title = f"Automappa: {sample_name}"
    app.run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
