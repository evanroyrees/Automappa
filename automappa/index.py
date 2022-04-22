#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging

from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc

from automappa.settings import server
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
        "--storage-type",
        help=(
            "The type of the web storage. (default: %(default)s)\n"
            "- memory: only kept in memory, reset on page refresh.\n"
            "- session: data is cleared once the browser quit.\n"
            "- local: data is kept after the browser quit.\n"
        ),
        choices=["memory", "session", "local"],
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
    args = parser.parse_args()

    # contig_marker_symbols_store = dcc.Store(
    #     id="contig-marker-symbols-store",
    #     storage_type=args.storage_type,
    #     data=contig_marker_symbols.to_json(orient="split"),
    #     clear_data=args.clear_store_data,
    # )
    binning_main_upload_store = dcc.Store(
        id="binning-main-upload-store",
        storage_type=args.storage_type,
        clear_data=args.clear_store_data,
    )
    markers_upload_store = dcc.Store(
        id="markers-upload-store",
        storage_type=args.storage_type,
        clear_data=args.clear_store_data,
    )
    metagenome_upload_store = dcc.Store(
        id="metagenome-upload-store",
        storage_type=args.storage_type,
        clear_data=args.clear_store_data,
    )
    samples_store = dcc.Store(
        id="samples-store",
        storage_type=args.storage_type,
        clear_data=args.clear_store_data,
    )
    selected_samples_store = dcc.Store(
        id="selected-tables-store",
        storage_type=args.storage_type,
        clear_data=args.clear_store_data,
    )

    if args.clear_store_data:
        logger.info(
            f"Store data cleared. Now re-run automappa *without* --clear-store-data"
        )
        exit()

    home_tab = dbc.Tab(label="Home", tab_id="home")
    refinement_tab = dbc.Tab(label="MAG Refinement", tab_id="mag_refinement")
    summary_tab = dbc.Tab(label="MAG Summary", tab_id="mag_summary")

    app.layout = dbc.Container(
        [
            # dbc.Col(markers_store),
            # dbc.Col(metagenome_annotations_store),
            # dbc.Col(refinement_data_store),
            # dbc.Col(contig_marker_symbols_store),
            dbc.Col(binning_main_upload_store),
            dbc.Col(markers_upload_store),
            dbc.Col(metagenome_upload_store),
            dbc.Col(samples_store),
            dbc.Col(selected_samples_store),
            # Navbar
            dbc.Tabs(
                id="tabs",
                children=[home_tab, refinement_tab, summary_tab],
                className="nav-fill",
            ),
            # html.Div(browser_storage_toast),
            html.Div(id="tab-content"),
        ],
        fluid=True,
    )

    # TODO: Replace cli inputs (as well as updating title once file is uploaded...)
    # dcc.Upload(id='metagenome-annotations-upload', children=dbc.Button("Upload annotations"))
    # dcc.Upload(id='markers-upload', children=dbc.Button("Upload annotations"))
    # sample_name = os.path.basename(args.binning_main).replace(" ", "_").split(".")[0]
    # app.title = f"Automappa: {sample_name}"
    app.title = "Automappa"
    app.run_server(host=server.host, port=server.port, debug=server.debug)


if __name__ == "__main__":
    main()
