# -*- coding: utf-8 -*-
import math
from typing import Any, Dict

import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
from plotly import graph_objects as go

from app import app

from apps.functions import get_assembly_stats

JSONDict = Dict[str, Any]
colors = {"background": "#F3F6FA", "background_div": "white"}

# return html Table with dataframe values
def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])]
        +
        # Body
        [
            html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
            for i in range(len(df))
        ]
    )


# returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [
            html.P(text, className="twelve columns indicator_text"),
            html.Pre(id=id_value, className="indicator_value"),
        ],
        className="two columns indicator",
    )


def bin_dropdown(df, column):
    options = [{"label": bin, "value": bin} for bin in df[column].unique()]
    return options


def plot_pie_chart(taxonomy: JSONDict, rank: str) -> Dict:
    df = pd.read_json(taxonomy, orient="split")
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

layout = [
    # Markdown Summary Report
    html.Div(
        className="row twelve columns",
        children=[
            html.Div(
                [
                    html.H5("Autometa Binning Report:", id="markdown_summary"),
                ],
                className="six columns",
            ),
            html.Div(
                [
                    indicator(
                        color="#00cc96",
                        text="Summary",
                        id_value="summary_indicator",
                    ),
                ],
                className="six columns",
            ),
        ],
    ),
    # Charts
    html.Div(
        [
            # Completeness Purity
            html.Div(
                [
                    html.P("Completeness & Purity"),
                    dcc.Graph(
                        id="bins_completness_purity",
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "98%"},
                    ),
                ],
                className="six columns chart_div",
            ),
            # Bin Taxa Breakdown
            html.Div(
                [
                    html.P("Bin Taxa Breakdown"),
                    dcc.Graph(
                        id="bin_taxa_breakdown",
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "98%"},
                    ),
                ],
                className="six columns chart_div",
            ),
        ],
        className="row",
        style={"marginTop": "5px"},
    ),
    # dropdowns
    html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="bin_summary_cluster_col",
                    options=[
                        {"label": "Cluster", "value": "cluster"},
                        {
                            "label": "Decision Tree Classifier",
                            "value": "ML_expanded_clustering",
                        },
                        {
                            "label": "Paired-end Refinement",
                            "value": "paired_end_refined_bin",
                        },
                    ],
                    value="cluster",
                    clearable=False,
                ),
                className="six columns",
                style={"float": "left"},
            ),
            html.Div(
                dcc.Dropdown(
                    id="taxa_by_rank_dropdown",
                    options=[
                        {"label": "Kingdom", "value": "kingdom"},
                        {"label": "Phylum", "value": "phylum"},
                        {"label": "Class", "value": "class"},
                        {"label": "Order", "value": "order"},
                        {"label": "Family", "value": "family"},
                        {"label": "Genus", "value": "genus"},
                        {"label": "Species", "value": "species"},
                    ],
                    value="phylum",
                    clearable=False,
                ),
                className="three columns",
                style={"float": "right"},
            ),
            html.Div(
                dcc.Dropdown(
                    id="bin_dropdown",
                    clearable=False,
                ),
                className="three columns",
                style={"floart": "right"},
            ),
        ],
        className="row",
        style={},
    ),
    # Taxa Heterogeneity chart and assembly stats table
    html.Div(
        [
            # Taxa Heterogeneity
            html.Div(
                [
                    html.P("Taxa Heterogeneity"),
                    dcc.Graph(
                        id="taxa_by_rank",
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "98%"},
                    ),
                ],
                className="six columns chart_div",
            ),
            # Assembly Stats Table
            html.Div(
                [
                    html.P(
                        "Assembly Statistics",
                        style={
                            "color": "#2a3f5f",
                            "fontSize": "13px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="assembly_stats",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    ),
                ],
                className="six columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
        ],
        className="row",
        style={"marginTop": "5px"},
    ),
]


@app.callback(
    Output("summary_indicator", "children"),
    [
        Input("bin_summary_cluster_col", "value"),
        Input("binning_df", "children"),
    ],
)
def summary_indicator(clusterCol, df):
    """
    Writes
    Given dataframe and cluster column:
    Input:
        - binning dataframe
        - binning column
    Returns:
        n_unique_bins - number of unique bins
    """
    df = pd.read_json(df, orient="split")
    df.set_index(clusterCol, inplace=True)
    df.drop("unclustered", inplace=True)
    n_unique_bins = df.index.nunique()
    clusters = dict(list(df.groupby(clusterCol)))
    completeness_list, purities = [], []
    markers = 139
    for cluster, dff in clusters.items():
        # This will be gene marker set to alter later
        pfams = dff.single_copy_PFAMs.dropna().tolist()
        all_pfams = [p for pfam in pfams for p in pfam.split(",")]
        total = len(all_pfams)
        nunique = len(set(all_pfams))
        completeness = float(nunique) / markers * 100
        completeness_list.append(completeness)
        purity = 0 if total == 0 else float(nunique) / total * 100
        purities.append(purity)
    median_completeness = round(np.median(completeness_list), 2)
    median_purity = round(np.median(purities), 2)
    txt = "\n".join(
        [
            "",
            "Bins: {}".format(n_unique_bins),
            "Median Completeness: {}".format(median_completeness),
            "Median Purity: {}".format(median_purity),
        ]
    )
    return txt


@app.callback(
    Output("bins_completness_purity", "figure"),
    [
        Input("bin_summary_cluster_col", "value"),
        Input("binning_df", "children"),
    ],
)
def bins_completness_purity(clusterCol, df):
    df = pd.read_json(df, orient="split")
    markers = 139
    clusters = dict(list(df.groupby(clusterCol)))
    cluster_names = []
    purities = []
    completes = []
    for cluster in clusters:
        pfams = clusters[cluster].single_copy_PFAMs.dropna().tolist()
        all_pfams = [p for pfam in pfams for p in pfam.split(",")]
        total = len(all_pfams)
        nunique = len(set(all_pfams))
        completeness = float(nunique) / markers * 100
        purity = float(nunique) / total * 100
        completes.append(completeness)
        purities.append(purity)
        cluster_names.append(cluster)
    return {
        "data": [
            {"x": cluster_names, "y": completes, "type": "bar", "name": "Completeness"},
            {"x": cluster_names, "y": purities, "type": "bar", "name": "Purity"},
        ],
        "layout": {"animate": True},
    }


@app.callback(
    Output("bin_taxa_breakdown", "figure"),
    [
        Input("taxa_by_rank_dropdown", "value"),
        Input("taxonomy_df", "children"),
    ],
)
def bin_taxa_breakdown(taxonomy, selected_rank):
    return plot_pie_chart(taxonomy, selected_rank)


@app.callback(
    Output("bin_dropdown", "options"),
    [
        Input("bin_summary_cluster_col", "value"),
        Input("binning_df", "children"),
    ],
)
def bin_dropdown(clusterCol, df):
    df = pd.read_json(df, orient="split")
    return bin_dropdown(df, clusterCol)


@app.callback(
    Output("taxa_by_rank", "figure"),
    [
        Input("taxa_by_rank_dropdown", "value"),
        Input("bin_summary_cluster_col", "value"),
        Input("binning_df", "children"),
    ],
)
def taxa_by_rank(rank, clusterCol, df):
    df = pd.read_json(df, orient="split")
    return taxa_by_rank(df, clusterCol, rank)


@app.callback(
    Output("assembly_stats", "children"),
    [Input("bin_summary_cluster_col", "value"), Input("binning_df", "children")],
)
def assembly_stats(clusterCol, df):
    df = pd.read_json(df, orient="split")
    stats_df = get_assembly_stats(df, clusterCol)
    return df_to_table(stats_df)
