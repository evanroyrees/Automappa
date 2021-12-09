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


mag_summary_stats_datatable = html.Div(id="mag-summary-stats-datatable")

mag_summary_cluster_col_dropdown = dcc.Dropdown(
    id="mag-summary-cluster-col-dropdown",
    value="cluster",
    clearable=False,
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


########################################################################
# LAYOUT
# ######################################################################

# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
# For best results, make sure you adhere to the following two rules when constructing your layouts:
#
# 1. Only use Row and Col inside a Container.
# 2. The immediate children of any Row component should always be Col components.
# 3. Your content should go inside the Col components.


layout = dbc.Container(
    [
        dbc.Col(mag_summary_cluster_col_dropdown),
        dbc.Row(dbc.Col(mag_summary_stats_datatable)),
    ],
    fluid=True,
)


@app.callback(
    Output("summary_indicator", "children"),
    [
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("metagenome-annotations", "children"),
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
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("metagenome-annotations", "children"),
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
        Input("mag-summary-cluster-col-dropdown", "value"),
        Input("metagenome-annotations", "children"),
    ],
)
def bin_dropdown(clusterCol, df):
    df = pd.read_json(df, orient="split")
    return bin_dropdown(df, clusterCol)


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
def mag_summary_stats_datatable_callback(df, markers_json, cluster_col):
    bin_df = pd.read_json(df, orient="split")
    markers = pd.read_json(markers_json, orient="split").set_index("contig")
    # TODO:COMBAK:FIXME: read in markers from json (or convert to appropriate format...)
    # TODO: Render summary table...
    # Re-install autometa and push changes to autometa.binning.summary.get_metabin_stats(...)
    if cluster_col not in bin_df:
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
    return DataTable(
        data=stats_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in stats_df.columns],
        style_cell={"textAlign": "center"},
        virtualization=False,
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
