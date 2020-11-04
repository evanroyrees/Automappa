# -*- coding: utf-8 -*-
import math

import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go

from app import app, indicator, df_to_table

colors = {"background": "#F3F6FA", "background_div": "white"}


def bin_dropdown(df, column):
    options = [{"label": bin, "value": bin} for bin in df[column].unique()]
    return options


def pie_chart(df, column, rank, bin):
    if not bin:
        layout = dict(
            annotations=[
                dict(
                    text="Select bin from dropdown for taxa breakdown", showarrow=False
                )
            ]
        )
        return {"data": [], "layout": layout}
    dff = df[df[column] == bin]
    n_ctgs = len(dff.index)
    values = [float(c) / n_ctgs for c in dff.groupby(rank)[rank].count().tolist()]
    labels = dff.groupby(rank)[rank].count().index.tolist()
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


def cases_by_period(df, period, priority, origin):
    df = df.dropna(subset=["Type", "Reason", "Origin"])
    stages = df["Type"].unique()

    # priority filtering
    if priority != "all_p":
        df = df[df["Priority"] == priority]

    # period filtering
    df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")
    if period == "W-MON":
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"]) - pd.to_timedelta(
            7, unit="d"
        )
    df = df.groupby([pd.Grouper(key="CreatedDate", freq=period), "Type"]).count()

    dates = df.index.get_level_values("CreatedDate").unique()
    dates = [str(i) for i in dates]

    co = {  # colors for stages
        "Electrical": "#264e86",
        "Other": "#0074e4",
        "Structural": "#74dbef",
        "Mechanical": "#eff0f4",
        "Electronic": "rgb(255, 127, 14)",
    }

    data = []
    for stage in stages:
        stage_rows = []
        for date in dates:
            try:
                row = df.loc[(date, stage)]
                stage_rows.append(row["IsDeleted"])
            except Exception as e:
                stage_rows.append(0)

        data_trace = go.Bar(
            x=dates, y=stage_rows, name=stage, marker=dict(color=co[stage])
        )
        data.append(data_trace)

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=40, r=25, b=40, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


def cases_by_account(cases):
    cases = cases.dropna(subset=["AccountId"])
    cases = pd.merge(cases, accounts, left_on="AccountId", right_on="Id")
    cases = cases.groupby(["AccountId", "Name"]).count()
    cases = cases.sort_values("IsDeleted")
    data = [
        go.Bar(
            y=cases.index.get_level_values("Name"),
            x=cases["IsDeleted"],
            orientation="h",
        )
    ]  # x could be any column value since its a count

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


def taxa_by_rank(df, column, rank):
    ranks = {
        "kingdom": "Kingdom",
        "phylum": "Phylum",
        "class": "Class",
        "order": "Order",
        "family": "Family",
        "genus": "Genus",
        "species": "Species",
    }
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


def assembly_stats(df, column):
    metrics = {"n50": {}, "clusters": {}}
    bins = dict(list(df.groupby(column)))
    for cluster, dff in bins.items():
        # 1. Determine cluster n50
        lengths = sorted(dff.length.tolist(), reverse=True)
        half_size = dff.length.sum() / 2
        total, n50 = 0, None
        for l in lengths:
            total += l
            if total >= half_size:
                n50 = l
                break
        metrics["n50"].update({cluster: n50})
        metrics["clusters"].update({cluster: cluster})
    ftuples = [("n_ctgs", "count"), ("size", "sum"), ("max_len", "max")]
    clusters = df.groupby(column)
    agg_stats = clusters["length"].agg(ftuples)
    metrics.update(agg_stats.to_dict())
    # Get weighted averages of GC percentages
    get_gc_wtdavg = lambda g: round(
        np.average(g["gc"], weights=(g.length / g.length.sum())), 2
    )
    wtd_gcs = clusters.apply(get_gc_wtdavg)
    # Get weighted standard deviation
    get_wtd_gcs_sdpc = lambda g: round(
        (
            math.sqrt(
                np.average(
                    (g["gc"] - np.average(g["gc"], weights=(g.length / g.length.sum())))
                    ** 2,
                    weights=(g.length / g.length.sum()),
                )
            )
            / np.average(g["gc"], weights=(g.length / g.length.sum()))
        )
        * 100,
        2,
    )
    wtd_gcs_sdpc = clusters.apply(get_wtd_gcs_sdpc)
    # weighted_gc_sdpc = (weighted_gc_stdev / weighted_gc_av)*100
    metrics.update(
        {"wtd_gcs": wtd_gcs.to_dict(), "wtd_gc_sdpc": wtd_gcs_sdpc.to_dict()}
    )

    # Get weighted average of Coverages
    get_cov_wtdavg = lambda g: round(
        np.average(g["cov"], weights=(g.length / g.length.sum())), 2
    )
    wtd_covs = clusters.apply(get_cov_wtdavg)
    # Get weighted standard deviation and calculate z-score...
    get_wtd_covs_sdpc = lambda g: round(
        (
            math.sqrt(
                np.average(
                    (
                        g["cov"]
                        - np.average(g["cov"], weights=(g.length / g.length.sum()))
                    )
                    ** 2,
                    weights=(g.length / g.length.sum()),
                )
            )
            / np.average(g["cov"], weights=(g.length / g.length.sum()))
        )
        * 100,
        2,
    )
    wtd_covs_sdpc = clusters.apply(get_wtd_covs_sdpc)
    metrics.update(
        {"wtd_covs": wtd_covs.to_dict(), "wtd_cov_sdpc": wtd_covs_sdpc.to_dict()}
    )
    bin_df = pd.DataFrame(
        {
            "cluster": metrics["clusters"],
            "size": metrics["size"],
            "longest_contig": metrics["max_len"],
            "n50": metrics["n50"],
            "number_contigs": metrics["n_ctgs"],
            "wtd_cov": metrics["wtd_covs"],
            "wtd_cov_sdpc": metrics["wtd_cov_sdpc"],
            "wtd_gc": metrics["wtd_gcs"],
            "wtd_gc_sdpc": metrics["wtd_gc_sdpc"],
        }
    )
    return df_to_table(bin_df)


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
def summary_indicator_callback(clusterCol, df):
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
def bins_completness_purity_callback(clusterCol, df):
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
        Input("bin_dropdown", "value"),
        Input("taxa_by_rank_dropdown", "value"),
        Input("bin_summary_cluster_col", "value"),
        Input("binning_df", "children"),
    ],
)
def bin_taxa_breakdown_callback(selectedBin, selectedRank, clusterCol, df):
    df = pd.read_json(df, orient="split")
    return pie_chart(df, clusterCol, selectedRank, selectedBin)


@app.callback(
    Output("bin_dropdown", "options"),
    [
        Input("bin_summary_cluster_col", "value"),
        Input("binning_df", "children"),
    ],
)
def bin_dropdown_callback(clusterCol, df):
    df = pd.read_json(df, orient="split")
    return bin_dropdown(df, clusterCol)


@app.callback(
    Output("cases_by_period", "figure"),
    [
        Input("cases_period_dropdown", "value"),
        Input("origin_dropdown", "value"),
        Input("priority_dropdown", "value"),
        Input("cases_df", "children"),
    ],
)
def cases_period_callback(period, origin, priority, df):
    df = pd.read_json(df, orient="split")
    return cases_by_period(df, period, priority, origin)


@app.callback(
    Output("taxa_by_rank", "figure"),
    [
        Input("taxa_by_rank_dropdown", "value"),
        Input("bin_summary_cluster_col", "value"),
        Input("binning_df", "children"),
    ],
)
def taxa_by_rank_callback(rank, clusterCol, df):
    df = pd.read_json(df, orient="split")
    return taxa_by_rank(df, clusterCol, rank)


@app.callback(
    Output("cases_by_account", "figure"),
    [
        Input("cases_df", "children"),
    ],
)
def cases_account_callback(df):
    df = pd.read_json(df, orient="split")
    return cases_by_account(df)


# updates top lost opportunities based on df updates
@app.callback(
    Output("assembly_stats", "children"),
    [Input("bin_summary_cluster_col", "value"), Input("binning_df", "children")],
)
def assembly_stats_callback(clusterCol, df):
    df = pd.read_json(df, orient="split")
    return assembly_stats(df, clusterCol)


# @app.callback(Output("cases_modal", "style"), [Input("new_case", "n_clicks")])
# def display_cases_modal_callback(n):
#     if n > 0:
#         return {"display": "block"}
#     return {"display": "none"}
#
#
# @app.callback(
#     Output("new_case", "n_clicks"),
#     [Input("cases_modal_close", "n_clicks"), Input("submit_new_case", "n_clicks")],
# )
# def close_modal_callback(n, n2):
#     return 0


# @app.callback(
#     Output("cases_df", "children"),
#     [Input("submit_new_case", "n_clicks")],
#     [
#         State("new_case_account", "value"),
#         State("new_case_origin", "value"),
#         State("new_case_reason", "value"),
#         State("new_case_subject", "value"),
#         State("new_case_contact", "value"),
#         State("new_case_type", "value"),
#         State("new_case_status", "value"),
#         State("new_case_description", "value"),
#         State("new_case_priority", "value"),
#         State("cases_df", "children"),
#     ],
# )
# def add_case_callback(
#     n_clicks, account_id, origin, reason, subject, contact_id, case_type, status, description, priority, current_df
#     ):
#     if n_clicks > 0:
#         query = {
#             "AccountId": account_id,
#             "Origin": origin,
#             "Reason": reason,
#             "Subject": subject,
#             "ContactId": contact_id,
#             "Type": case_type,
#             "Status": status,
#             "Description": description,
#             "Priority": priority,
#         }
#
#         # am_manager.add_case(query)
#         # df = am_manager.get_cases()
#         return df.to_json(orient="split")
#
#     return current_df
