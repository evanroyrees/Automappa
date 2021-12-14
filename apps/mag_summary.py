# -*- coding: utf-8 -*-
from typing import Any, Dict

import numpy as np
import pandas as pd

from autometa.binning.summary import fragmentation_metric, get_metabin_stats

from dash import dcc, html
from dash.dash_table import DataTable
from dash.dependencies import Input, Output
from plotly import graph_objects as go
import dash_bootstrap_components as dbc

from app import app


JSONDict = Dict[str, Any]
colors = {"background": "#F3F6FA", "background_div": "white"}


########################################################################
# COMPONENTS: Figures & Tables
# ######################################################################


metric_boxplot = dcc.Loading(id="loading-mag-metrics-boxplot",children=[dcc.Graph(id="mag-metrics-boxplot")], type="graph")

mag_summary_stats_datatable = dcc.Loading(id="loading-mag-summary-stats-datatable",children=[html.Div(id="mag-summary-stats-datatable")], type="circle")

mag_summary_cluster_col_dropdown = dcc.Dropdown(
    id="mag-summary-cluster-col-dropdown",
    value="cluster",
    clearable=False,
)

###
# AESTHETHIC COMPONENTS: Dropdowns
###

# mag_selection_dropdown = html.Div(dcc.Dropdown(id="mag-selection-dropdown", value="STuff", clearable=True))


def plot_pie_chart(df: pd.DataFrame, rank: str) -> Dict:
    total_contigs = df.shape[0]
    values = [
        contig / total_contigs for contig in df.groupby(rank)[rank].count().tolist()
    ]
    labels = df.groupby(rank)[rank].count().index.tolist()
    layout = go.Layout(
        margin=dict(l=0, r=0, b=0, t=4, pad=8),
        legend=dict(orientation="h"),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    trace = go.Pie(
        labels=labels,
        values=values,
        hoverinfo="label+percent",
        textinfo="label",
        showlegend=False,
    )
    return {"data": [trace], "layout": layout}


def taxonomy_sankey_diagram():
    return [
        html.Label("Figure 3: Taxonomic Distribution"),
        dcc.Graph(id="taxonomy-distribution"),
    ]


def taxa_by_rank(df, column, rank):
    clusters = dict(list(df.groupby(column)))
    clusters = df[column].unique().tolist()
    clusters.pop(clusters.index("unclustered"))
    nuniques = [df[df[column] == cluster][rank].nunique() for cluster in clusters]
    data = [
        go.Bar(y=clusters, x=nuniques, orientation="h")
    ]  # x could be any column value since its a count

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


########################################################################
# LAYOUT
# ######################################################################

# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
# For best results, make sure you adhere to the following two rules when constructing your layouts:
#
# 1. Only use Row and Col inside a Container.
# 2. The immediate children of any Row component should always be Col components.
# 3. Your content should go inside the Col components.

# Markdown Summary Report
## Bin Taxa Breakdown ==> dcc.Graph(id="bin_taxa_breakdown")
## sankey diagram for specific mag selection dcc.Graph(id="taxa_by_rank")

### Dropdowns
# canonical_rank ==> dcc.Dropdown(id="taxa_by_rank_dropdown")

# TODO: Add dbc.Col(mag_selection_dropdown)
layout = dbc.Container(
    [
        dbc.Col(metric_boxplot),
        dbc.Row([dbc.Col(mag_summary_cluster_col_dropdown)]),
        dbc.Col(mag_summary_stats_datatable),
    ],
    fluid=True,
)


########################################################################
# CALLBACKS
# ######################################################################


@app.callback(
    Output("mag-metrics-boxplot", "figure"),
    [
        Input("metagenome-annotations", "children"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_metrics_boxplot_callback(df_json, cluster_col):
    """
    Writes
    Given dataframe as json and cluster column:
    Input:
        - binning dataframe
        - binning column
    Returns:
        n_unique_bins - number of unique bins
    """
    mag_summary_df = pd.read_json(df_json, orient="split")
    mag_summary_df = mag_summary_df.dropna(subset=[cluster_col])
    mag_summary_df = mag_summary_df.loc[mag_summary_df[cluster_col].ne("unclustered")]
    return go.Figure(
        data=[
            go.Box(y=mag_summary_df.completeness, name="Completeness", boxmean=True),
            go.Box(y=mag_summary_df.purity, name="Purity", boxmean=True),
        ]
    )


@app.callback(
    Output("mag-taxonomy-sankey", "figure"),
    [
        Input("metagenome-annotations", "children"),
    ],
)
def mag_taxonomy_sankey_callback(mag_summary_json):
    # NOTE: Majority vote will need to first be performed (or CheckM summary parsed...)
    # pd.DataFrame should have cluster (index) and cluster metrics/stats (cols)
    # e.g. completeness, purity, taxonomies, assembly stats, etc.
    mag_summary_df = pd.read_json(mag_summary_json, orient="split")
    ranks = ["superkingdom", "phylum", "class", "order", "family", "genus", "species"]
    taxa_df = mag_summary_df[ranks].fillna("unclassified")
    # Add canonical rank prefixes so we do not get any cycles
    for rank in ranks:
        if rank in taxa_df:
            taxa_df[rank] = taxa_df[rank].map(
                lambda x: f"{rank[0]}_{x}" if rank != "superkingdom" else f"d_{x}"
            )
    # Build list of labels in order of ranks
    label = []
    for rank in ranks:
        label.extend(taxa_df[rank].unique().tolist())
    # Build paths in order of ranks
    source = []
    target = []
    value = []
    # Iterate through paths from superkingdom to species
    for rank in ranks:
        # iterate through sources at level
        for rank_name, rank_df in taxa_df.groupby(rank):
            label_idx = label.index(rank_name)
            next_rank_idx = ranks.index(rank) + 1
            if next_rank_idx >= len(ranks):
                continue
            next_rank = ranks[next_rank_idx]
            # iterate through targets
            # all source is from label rank name index
            for rank_n in rank_df[next_rank].unique():
                target_index = label.index(rank_n)
                value_count = len(rank_df[rank_df[next_rank] == rank_n])
                label.append(label_idx)
                source.append(label_idx)
                target.append(target_index)
                value.append(value_count)
    return go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=8,
                    thickness=13,
                    line=dict(width=0.3),
                    label=label,
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                ),
            )
        ]
    )


@app.callback(
    Output("bin_taxa_breakdown", "figure"),
    [
        Input("taxa_by_rank_dropdown", "value"),
        Input("taxonomy_df", "children"),
    ],
)
def bin_taxa_breakdown(taxonomy, selected_rank):
    df = pd.read_json(taxonomy, orient="split")
    return plot_pie_chart(df, selected_rank)


@app.callback(
    Output("mag-selection-dropdown", "options"),
    [
        Input("metagenome-annotations", "children"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def bin_dropdown_options_callback(mag_annotations_json, cluster_col):
    df = pd.read_json(mag_annotations_json, orient="split")
    if cluster_col not in df.columns:
        return [{"label": "", "value": ""}]
    return [{"label": bin, "value": bin} for bin in df[cluster_col].unique()]


@app.callback(
    Output("taxa_by_rank", "figure"),
    [
        Input("taxa_by_rank_dropdown", "value"),
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("metagenome-annotations", "children"),
    ],
)
def taxa_by_rank(rank, clusterCol, df):
    df = pd.read_json(df, orient="split")
    return taxa_by_rank(df, clusterCol, rank)


@app.callback(
    Output("mag-summary-stats-datatable", "children"),
    [
        Input("metagenome-annotations", "children"),
        Input("kingdom-markers", "children"),
        Input("mag-summary-cluster-col-dropdown", "value"),
    ],
)
def mag_summary_stats_datatable_callback(
    mag_annotations_json, markers_json, cluster_col
):
    bin_df = pd.read_json(mag_annotations_json, orient="split")
    markers = pd.read_json(markers_json, orient="split").set_index("contig")
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
                    "completeness": pd.NA,
                    "purity": pd.NA,
                    "num_total_markers": total_markers,
                    f"num_unique_markers (expected {num_expected_markers})": num_markers_present,
                    "num_single_copy_markers": num_single_copy_markers,
                }
            ]
        ).convert_dtypes()
    else:
        stats_df = get_metabin_stats(
            bin_df=bin_df, markers=markers, cluster_col=cluster_col
        ).reset_index()
    stats_df = stats_df.fillna("NA").round(2)
    stats_df = stats_df.drop(columns=["size_pct", "seqs_pct"], errors="ignore")
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


@app.callback(
    Output("mag-summary-cluster-col-dropdown", "options"),
    [Input("metagenome-annotations", "children")],
)
def mag_summary_cluster_col_dropdown_options_callback(df_json):
    bin_df = pd.read_json(df_json, orient="split")
    return [
        {"label": col.title(), "value": col}
        for col in bin_df.columns
        if "cluster" in col or "refinement" in col
    ]
