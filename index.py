#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from app import app, gc_length_dataframe_from_fasta, load_markers
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


def layout(
    binning: pd.DataFrame,
    markers: pd.DataFrame,
    taxonomy: pd.DataFrame,
    annotations: pd.DataFrame,
):
    cluster_columns = [
        col
        for col in binning.columns
        if "refinement_" in col or "cluster" in col or "contig" in col
    ]
    
    app.layout = html.Div(
        [
            #### Send data to hidden divs for use in explorer.py and summary.py
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
                taxonomy.to_json(orient="split"),
                id="metagenome-taxonomy",
                style={"display": "none"},
            ),
            html.Div(
                annotations.to_json(orient="split"),
                id="metagenome-annotations",
                style={"display": "none"},
            ),
            html.Div(
                binning[cluster_columns].to_json(orient="split"),
                id="refinement-data",
                style={"display": "none"},
            ),
            #### Add links to external style sheets
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
            #### Navbar div with Automappa tabs and School Logo
            html.Div(
                [
                    html.Label(
                        "Automappa Dashboard", className="three columns app-title"
                    ),
                    html.Div(
                        [
                            dcc.Tabs(
                                id="tabs",
                                style={"height": "10", "verticalAlign": "middle"},
                                children=[
                                    dcc.Tab(
                                        label="Refine Bins",
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
            #### Below Navbar where we render selected tab content
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

    parser = argparse.ArgumentParser(
        description="Automappa: An interactive interface for exploration of metagenomes"
    )
    parser.add_argument(
        "--binning",
        help="Path to binning.tsv",
        required=True,
    )
    parser.add_argument(
        "--kmers",
        help="Path to embedded kmers.tsv",
        required=True,
    )
    parser.add_argument(
        "--coverages",
        help="Path to coverages.tsv",
        required=True,
    )
    parser.add_argument(
        "--fasta",
        help="Path to metagenome.fasta",
        required=True,
    )
    parser.add_argument(
        "--markers",
        help="Path to `kingdom`.markers.tsv",
        required=True,
    )
    parser.add_argument(
        "--taxonomy",
        help="Path to taxonomy.tsv",
        required=True,
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
    binning = pd.read_csv(args.binning, sep="\t")
    # Needed for completeness/purity calculations
    markers = load_markers(args.markers)
    # Store for taxonomy vizualizations
    taxonomy = pd.read_csv(args.taxonomy, sep="\t")
    # Store these annotations together, b/c they will be used for same visualizations
    kmers = pd.read_csv(args.kmers, sep="\t")
    coverages = pd.read_csv(args.coverages, sep="\t")
    annotations = gc_length_dataframe_from_fasta(args.fasta)
    # binning and taxonomy are added here to color contigs
    # Kingdom-specific Binning will subset entire dataframe to kingdom binned.
    for annotation in [kmers, coverages, binning, taxonomy]:
        annotations = pd.merge(annotations, annotation, on="contig", how="inner")

    print(f"binning shape:\t\t{binning.shape}")
    print(f"markers shape:\t\t{markers.shape}")
    print(f"taxonomy shape:\t\t{taxonomy.shape}")
    print(f"annotations shape:\t{annotations.shape}")

    print("Data loaded. It may take a minute or two to construct all interactive graphs...")
    layout(binning=binning, markers=markers, taxonomy=taxonomy, annotations=annotations)

    app.run_server(host=args.host, port=args.port, debug=args.debug)
