#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import logging

from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from autometa.common.markers import load as load_markers

from automappa.utils.markers import (
    convert_marker_counts_to_marker_symbols,
    get_contig_marker_counts,
)

from automappa.apps import home, mag_refinement, mag_summary
from automappa.app import app

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)



@app.callback(Output("tab-content", "children"), [Input("tabs", "active_tab")])
def render_content(active_tab):
    layouts = {
        "home": home.layout,
        "mag_refinement": mag_refinement.layout,
        "mag_summary": mag_summary.layout,
    }
    return layouts.get(active_tab, "home")


def main():
    parser = argparse.ArgumentParser(
        description="Automappa: An interactive interface for exploration of metagenomes",
        formatter_class=argparse.RawTextHelpFormatter,
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
        "--port",
        help="port to expose. (default: %(default)s)",
        default=8050,
        type=int,
        metavar="number",
    )
    parser.add_argument(
        "--host",
        help="host ip address to expose. (default: %(default)s)",
        type=str,
        default="0.0.0.0",
        metavar="ip address",
    )
    parser.add_argument(
        "--storage-type",
        help=(
            "The type of the web storage. (default: %(default)s)\n"
            "- memory: only kept in memory, reset on page refresh.\n"
            "- session: data is cleared once the browser quit.\n"
            "- local: data is kept after the browser quit. (Currently not supported)\n"
        ),
        choices=["memory", "session"],
        default="session",
    )
    parser.add_argument(
        "--clear-store-data",
        help=(
            "Clear storage data (default: %(default)s)\n"
            "(only required if using 'session' or 'local' for `--storage-type`)"
        ),
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--debug",
        help="Turn on debug mode",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    logger.info("Please wait a moment while all of the data is loaded.")
    # Needed separately for binning refinement selections.
    binning = pd.read_csv(args.binning_main, sep="\t", low_memory=False)
    # Needed for completeness/purity calculations
    markers = load_markers(args.markers).reset_index().copy()

    # Check dataset size for dcc.Store(...) with browser limits...
    # For details see: https://stackoverflow.com/a/61018107 and https://arty.name/localstorage.html
    chrome_browser_quota = 5200000
    dataset_chars = len(binning.to_json(orient="split"))
    if dataset_chars >= chrome_browser_quota:
        logger.warning(f"{args.binning_main} exceeds browser storage limits ({dataset_chars} > {chrome_browser_quota}).")
        logger.warning("Persisting refinements is DISABLED!")

    # Metagenome Annotations Store
    metagenome_annotations_store = dcc.Store(
        id="metagenome-annotations",
        storage_type=args.storage_type,
        data=binning.to_json(orient="split"),
        clear_data=args.clear_store_data,
    )

    # Kingdom Markers Store
    markers_store = dcc.Store(
        id="markers-store",
        storage_type=args.storage_type,
        data=markers.to_json(orient="split"),
        clear_data=args.clear_store_data,
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

    refinement_data_store = dcc.Store(
        id="refinement-data",
        storage_type=args.storage_type,
        data=binning[binning_cols].to_json(orient="split"),
        clear_data=args.clear_store_data,
    )

    # Contig Marker Symbols Store
    contig_marker_counts = get_contig_marker_counts(
        binning.set_index("contig"), markers.set_index("contig")
    )
    contig_marker_symbols = convert_marker_counts_to_marker_symbols(
        contig_marker_counts
    ).reset_index()

    contig_marker_symbols_store = dcc.Store(
        id="contig-marker-symbols-store",
        storage_type=args.storage_type,
        data=contig_marker_symbols.to_json(orient="split"),
        clear_data=args.clear_store_data,
    )

    if args.clear_store_data:
        logger.info(f"Store data cleared. Now re-run automappa *without* --clear-store-data")
        exit()

    logger.info(f"binning shape:\t\t{binning.shape}")
    logger.info(f"markers shape:\t\t{markers.shape}")
    logger.info(
        "Data loaded. It may take a minute or two to construct all interactive graphs..."
    )

    home_tab = dbc.Tab(label="Home", tab_id="home")
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
                id="tabs",
                children=[home_tab, refinement_tab, summary_tab],
                className="nav-fill",
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
