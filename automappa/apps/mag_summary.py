# -*- coding: utf-8 -*-
from typing import Dict, List
from dash.exceptions import PreventUpdate

import numpy as np
import pandas as pd

from autometa.binning.summary import fragmentation_metric, get_metabin_stats

from dash import dcc, html
from dash.dash_table import DataTable
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from plotly import graph_objects as go
import plotly.io as pio

from automappa.app import app
from automappa.utils.figures import metric_barplot, taxonomy_sankey, metric_boxplot
from automappa.utils.serializers import get_table

pio.templates.default = "plotly_white"


########################################################################
# COMPONENTS: Figures & Tables
########################################################################

## Overview figures and table

mag_overview_metrics_boxplot = dcc.Loading(
    id="loading-mag-overview-metrics-boxplot",
    children=[
        dcc.Graph(
            id="mag-overview-metrics-boxplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="default",
    color="#0479a8",
)

mag_overview_gc_content_boxplot = dcc.Loading(
    id="loading-mag-overview-gc-content-boxplot",
    children=[
        dcc.Graph(
            id="mag-overview-gc-content-boxplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="dot",
    color="#646569",
)

mag_overview_length_boxplot = dcc.Loading(
    id="loading-mag-overview-length-boxplot",
    children=[
        dcc.Graph(
            id="mag-overview-length-boxplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="default",
    color="#0479a8",
)

mag_overview_coverage_boxplot = dcc.Loading(
    id="loading-mag-overview-coverage-boxplot",
    children=[
        dcc.Graph(
            id="mag-overview-coverage-boxplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="dot",
    color="#646569",
)

mag_summary_stats_datatable = [
    html.Label("Table 1. MAGs Summary"),
    dcc.Loading(
        id="loading-mag-summary-stats-datatable",
        children=[html.Div(id="mag-summary-stats-datatable")],
        type="circle",
        color="#646569",
    ),
]

### Selected MAG figures

mag_taxonomy_sankey = dcc.Loading(
    id="loading-mag-taxonomy-sankey",
    children=[dcc.Graph(id="mag-taxonomy-sankey")],
    type="graph",
)

mag_metrics_boxplot = dcc.Loading(
    id="loading-mag-metrics-barplot",
    children=[
        dcc.Graph(
            id="mag-metrics-barplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="dot",
    color="#646569",
)

mag_gc_content_boxplot = dcc.Loading(
    id="loading-mag-gc-content-boxplot",
    children=[
        dcc.Graph(
            id="mag-gc-content-boxplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="default",
    color="#0479a8",
)

mag_length_boxplot = dcc.Loading(
    id="loading-mag-length-boxplot",
    children=[
        dcc.Graph(
            id="mag-length-boxplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="dot",
    color="#646569",
)

mag_coverage_boxplot = dcc.Loading(
    id="loading-mag-coverage-boxplot",
    children=[
        dcc.Graph(
            id="mag-coverage-boxplot",
            config={"displayModeBar": False, "displaylogo": False},
        )
    ],
    type="default",
    color="#0479a8",
)

########################################################################
# AESTHETHIC COMPONENTS: Dropdowns
########################################################################


mag_summary_cluster_col_dropdown = [
    html.Label("MAG Summary Cluster Column Dropdown"),
    dcc.Dropdown(
        id="mag-summary-cluster-col-dropdown",
        value="cluster",
        placeholder="Select a cluster column to compute MAG summary metrics",
        clearable=False,
    ),
]

mag_selection_dropdown = [
    html.Label("MAG Selection Dropdown"),
    dcc.Dropdown(
        id="mag-selection-dropdown",
        clearable=True,
        placeholder="Select a MAG from this dropdown for a MAG-specific summary",
    ),
]


########################################################################
# LAYOUT
# ######################################################################

# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
# For best results, make sure you adhere to the following two rules when constructing your layouts:
#
# 1. Only use Row and Col inside a Container.
# 2. The immediate children of any Row component should always be Col components.
# 3. Your content should go inside the Col components.

# TODO: Markdown Summary Report

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(mag_overview_metrics_boxplot, width=3),
                dbc.Col(mag_overview_gc_content_boxplot, width=3),
                dbc.Col(mag_overview_length_boxplot, width=3),
                dbc.Col(mag_overview_coverage_boxplot, width=3),
            ]
        ),
        dbc.Row([dbc.Col(mag_summary_cluster_col_dropdown)]),
        dbc.Col(mag_summary_stats_datatable),
        dbc.Col(mag_selection_dropdown),
        dbc.Col(mag_taxonomy_sankey),
        dbc.Row(
            [
                dbc.Col(mag_metrics_boxplot, width=3),
                dbc.Col(mag_gc_content_boxplot, width=3),
                dbc.Col(mag_length_boxplot, width=3),
                dbc.Col(mag_coverage_boxplot, width=3),
            ]
        ),
    ],
    fluid=True,
)


########################################################################
# CALLBACKS
# ######################################################################


@app.callback(
    Output("mag-overview-metrics-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_overview_metrics_boxplot_callback(
    selected_tables_data: Dict[str, str], cluster_col: str
) -> go.Figure:
    """
    Writes
    Given dataframe as json and cluster column:
    Input:
        - binning dataframe
        - binning column
    Returns:
        n_unique_bins - number of unique bins
    """
    table_name = selected_tables_data["binning"]
    mag_summary_df = get_table(table_name)
    if cluster_col not in mag_summary_df.columns:
        raise PreventUpdate
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_summary_df = mag_summary_df.loc[mag_summary_df[cluster_col].ne("unclustered")]
    fig = metric_boxplot(df=mag_summary_df, metrics=["completeness", "purity"])
    return fig


@app.callback(
    Output("mag-overview-gc-content-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_overview_gc_content_boxplot_callback(
    selected_tables_data: Dict[str, str], cluster_col: str
) -> go.Figure:
    table_name = selected_tables_data["binning"]
    mag_summary_df = get_table(table_name)
    if cluster_col not in mag_summary_df.columns:
        raise PreventUpdate
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_summary_df = mag_summary_df.loc[mag_summary_df[cluster_col].ne("unclustered")]
    fig = metric_boxplot(df=mag_summary_df, metrics=["gc_content"])
    fig.update_traces(name="GC Content")
    return fig


@app.callback(
    Output("mag-overview-length-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_overview_length_boxplot_callback(
    selected_tables_data: Dict[str, str], cluster_col: str
) -> go.Figure:
    table_name = selected_tables_data["binning"]
    mag_summary_df = get_table(table_name)
    if cluster_col not in mag_summary_df.columns:
        raise PreventUpdate
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_summary_df = mag_summary_df.loc[mag_summary_df[cluster_col].ne("unclustered")]
    fig = metric_boxplot(mag_summary_df, metrics=["length"])
    return fig


@app.callback(
    Output("mag-overview-coverage-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_overview_coverage_boxplot_callback(
    selected_tables_data: Dict[str, str], cluster_col: str
) -> go.Figure:
    table_name = selected_tables_data["binning"]
    mag_summary_df = get_table(table_name)
    if cluster_col not in mag_summary_df.columns:
        raise PreventUpdate
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_summary_df = mag_summary_df.loc[mag_summary_df[cluster_col].ne("unclustered")]
    fig = metric_boxplot(mag_summary_df, metrics=["coverage"])
    return fig


@app.callback(
    Output("mag-summary-cluster-col-dropdown", "options"),
    [Input("selected-tables-store", "data")],
)
def mag_summary_cluster_col_dropdown_options_callback(selected_tables_data: Dict[str, str]):
    refinement_table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    refinement_df = get_table(refinement_table_name, index_col='contig')
    return [
        {"label": col.title(), "value": col}
        for col in refinement_df.columns
        if "cluster" in col or "refinement" in col
    ]


@app.callback(
    Output("mag-summary-stats-datatable", "children"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_summary_stats_datatable_callback(
    selected_tables_data: Dict[str, str], cluster_col:str
):
    binning_table_name = selected_tables_data["binning"]
    bin_df = get_table(binning_table_name, index_col='contig')
    refinement_table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    refinement_df = get_table(refinement_table_name, index_col='contig').drop(columns="cluster")
    bin_df = bin_df.join(refinement_df, how='right')
    markers_table_name = selected_tables_data["markers"]
    markers = get_table(markers_table_name, index_col="contig")
    if cluster_col not in bin_df.columns:
        num_expected_markers = markers.shape[1]
        length_weighted_coverage = np.average(
            a=bin_df.coverage, weights=bin_df.length / bin_df.length.sum()
        )
        length_weighted_gc = np.average(
            a=bin_df.gc_content, weights=bin_df.length / bin_df.length.sum()
        )
        cluster_pfams = markers[markers.index.isin(bin_df.index)]
        pfam_counts = cluster_pfams.sum()
        total_markers = pfam_counts.sum()
        num_single_copy_markers = pfam_counts[pfam_counts == 1].count()
        num_markers_present = pfam_counts[pfam_counts >= 1].count()
        stats_df = pd.DataFrame(
            [
                {
                    cluster_col: "metagenome",
                    "nseqs": bin_df.shape[0],
                    "size (bp)": bin_df.length.sum(),
                    "N90": fragmentation_metric(bin_df, quality_measure=0.9),
                    "N50": fragmentation_metric(bin_df, quality_measure=0.5),
                    "N10": fragmentation_metric(bin_df, quality_measure=0.1),
                    "length_weighted_gc_content": length_weighted_gc,
                    "min_gc_content": bin_df.gc_content.min(),
                    "max_gc_content": bin_df.gc_content.max(),
                    "std_gc_content": bin_df.gc_content.std(),
                    "length_weighted_coverage": length_weighted_coverage,
                    "min_coverage": bin_df.coverage.min(),
                    "max_coverage": bin_df.coverage.max(),
                    "std_coverage": bin_df.coverage.std(),
                    "num_total_markers": total_markers,
                    f"num_unique_markers (expected {num_expected_markers})": num_markers_present,
                    "num_single_copy_markers": num_single_copy_markers,
                }
            ]
        ).convert_dtypes()
    else:
        stats_df = (
            get_metabin_stats(
                bin_df=bin_df,
                markers=markers,
                cluster_col=cluster_col,
            )
            .reset_index()
            .fillna(0)
        )
    return DataTable(
        data=stats_df.to_dict("records"),
        columns=[
            {"name": col.replace("_", " "), "id": col} for col in stats_df.columns
        ],
        style_table={"overflowX": "auto"},
        style_cell={
            "height": "auto",
            # all three widths are needed
            "minWidth": "120px",
            "width": "120px",
            "maxWidth": "120px",
            "whiteSpace": "normal",
        },
        fixed_rows={"headers": True},
    )


## Selected MAG callbacks


@app.callback(
    Output("mag-taxonomy-sankey", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("mag-selection-dropdown", "value"),
    ],
)
def mag_taxonomy_sankey_callback(
    selected_tables_data: Dict[str,str], cluster_col: str, selected_mag: str
) -> go.Figure:
    binning_table_name = selected_tables_data["binning"]
    bin_df = get_table(binning_table_name, index_col='contig')
    refinement_table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    refinement_df = get_table(refinement_table_name, index_col='contig').drop(columns="cluster")
    bin_df = bin_df.join(refinement_df, how='right')
    if cluster_col not in bin_df.columns:
        raise PreventUpdate
    mag_df = bin_df.loc[bin_df[cluster_col].eq(selected_mag)]
    fig = taxonomy_sankey(mag_df)
    return fig


@app.callback(
    Output("mag-gc-content-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("mag-selection-dropdown", "value"),
    ],
)
def mag_summary_gc_content_boxplot_callback(
    selected_tables_data: Dict[str,str], cluster_col: str, selected_mag: str
) -> go.Figure:
    binning_table_name = selected_tables_data["binning"]
    bin_df = get_table(binning_table_name, index_col='contig')
    refinement_table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    refinement_df = get_table(refinement_table_name, index_col='contig').drop(columns="cluster")
    bin_df = bin_df.join(refinement_df, how='right')
    if cluster_col not in bin_df.columns:
        raise PreventUpdate
    bin_df = bin_df.dropna(subset=[cluster_col])
    mag_df = bin_df.loc[bin_df[cluster_col].eq(selected_mag)]
    mag_df = mag_df.round(2)
    fig = metric_boxplot(df=mag_df, metrics=["gc_content"])
    fig.update_traces(name="GC Content")
    return fig


@app.callback(
    Output("mag-metrics-barplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("mag-selection-dropdown", "value"),
    ],
)
def mag_metrics_callback(
    selected_tables_data: Dict[str,str], cluster_col: str, selected_mag: str
) -> go.Figure:
    if not selected_mag:
        raise PreventUpdate
    binning_table_name = selected_tables_data["binning"]
    bin_df = get_table(binning_table_name, index_col='contig')
    refinement_table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    refinement_df = get_table(refinement_table_name, index_col='contig').drop(columns="cluster")
    mag_summary_df = bin_df.join(refinement_df, how='right')
    if cluster_col not in mag_summary_df.columns:
        raise PreventUpdate
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_df = mag_summary_df.loc[mag_summary_df[cluster_col].eq(selected_mag)]
    mag_df = mag_df.round(2)
    fig = metric_barplot(df=mag_df, metrics=["completeness", "purity"], name=selected_mag)
    return fig


@app.callback(
    Output("mag-coverage-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("mag-selection-dropdown", "value"),
    ],
)
def mag_summary_gc_content_boxplot_callback(
    selected_tables_data: Dict[str,str], cluster_col: str, selected_mag: str
) -> go.Figure:
    if not selected_mag:
            raise PreventUpdate
    binning_table_name = selected_tables_data["binning"]
    bin_df = get_table(binning_table_name, index_col='contig')
    refinement_table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    refinement_df = get_table(refinement_table_name, index_col='contig').drop(columns="cluster")
    mag_summary_df = bin_df.join(refinement_df, how='right')
    if cluster_col not in mag_summary_df.columns:
        raise PreventUpdate
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_df = mag_summary_df.loc[mag_summary_df[cluster_col].eq(selected_mag)]
    mag_df = mag_df.round(2)
    fig = metric_boxplot(df=mag_df, metrics=["coverage"])
    return fig


@app.callback(
    Output("mag-length-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("mag-selection-dropdown", "value"),
    ],
)
def mag_summary_gc_content_boxplot_callback(
    selected_tables_data: Dict[str,str], cluster_col: str, selected_mag: str
) -> go.Figure:
    if not selected_mag:
            raise PreventUpdate
    binning_table_name = selected_tables_data["binning"]
    bin_df = get_table(binning_table_name, index_col='contig')
    refinement_table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    refinement_df = get_table(refinement_table_name, index_col='contig').drop(columns="cluster")
    mag_summary_df = bin_df.join(refinement_df, how='right')
    if cluster_col not in mag_summary_df.columns:
        raise PreventUpdate
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_df = mag_summary_df.loc[mag_summary_df[cluster_col].eq(selected_mag)]
    mag_df = mag_df.round(2)
    fig = metric_boxplot(df=mag_df, metrics=["length"])
    return fig


@app.callback(
    Output("mag-selection-dropdown", "options"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_selection_dropdown_options_callback(
    selected_tables_data: Dict[str,str], cluster_col: str
) -> List[Dict[str, str]]:
    table_name = selected_tables_data["binning"].replace("-binning", "-refinement")
    df = get_table(table_name, index_col="contig")
    if cluster_col not in df.columns:
        options = []
    else:
        options = [
            {"label": cluster, "value": cluster}
            for cluster in df[cluster_col].dropna().unique()
        ]
    return options
