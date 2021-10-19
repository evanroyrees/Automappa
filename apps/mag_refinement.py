# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

import dash_table
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
from dash import dcc
from dash import html

import dash_html_components as html
import dash_daq as daq
from plotly import graph_objs as go

from app import app


def marker_size_scaler(x: pd.DataFrame, scale_by: str = "length") -> int:
    x_min_scaler = x[scale_by] - x[scale_by].min()
    x_max_scaler = x[scale_by].max() - x[scale_by].min()
    if not x_max_scaler:
        # Protect Division by 0
        x_ceil = np.ceil(x_min_scaler / x_max_scaler + 1)
    else:
        x_ceil = np.ceil(x_min_scaler / x_max_scaler)
    x_scaled = x_ceil * 2 + 4
    return x_scaled


layout = [
    # Hidden div to store refinement selections
    html.Div(id="refinements-clusters", style={"display": "none"}),
    # 2D-scatter plot row div
    html.Div(
        [
            html.Div(
                [
                    html.Label("Figure 1: 2D Binning Overview"),
                    dcc.Graph(
                        id="scatterplot-2d",
                        style={"height": "90%", "width": "98%"},
                        clear_on_unhover=True,
                    ),
                ],
                className="ten columns chart_div",
            ),
            html.Div(
                [
                    html.Button(
                        "Download Refinements",
                        id="refinements-download-button",
                        n_clicks=0,
                        className="button button--primary",
                    ),
                    Download(id="refinements-download"),
                    html.Label("Color contigs by:"),
                    dcc.Dropdown(
                        id="color-by-column",
                        options=[],
                        value="cluster",
                        clearable=False,
                    ),
                    html.Label("X-Axis:"),
                    dcc.Dropdown(
                        id="x-axis-2d",
                        options=[
                            {"label": "X_1", "value": "x_1"},
                            {"label": "Coverage", "value": "coverage"},
                            {"label": "GC Content", "value": "gc_content"},
                            {"label": "Length", "value": "length"},
                        ],
                        value="x_1",
                        clearable=False,
                    ),
                    html.Label("Y-Axis:"),
                    dcc.Dropdown(
                        id="y-axis-2d",
                        options=[
                            {"label": "X_2", "value": "x_2"},
                            {"label": "Coverage", "value": "coverage"},
                            {"label": "GC Content", "value": "gc_content"},
                            {"label": "Length", "value": "length"},
                        ],
                        value="x_2",
                        clearable=False,
                    ),
                    html.Pre(
                        style={
                            "textAlign": "middle",
                        },
                        id="selection-binning-metrics",
                    ),
                    # add show-legend-toggle
                    daq.ToggleSwitch(
                        id="show-legend-toggle",
                        size=40,
                        color="#c5040d",
                        label="Show/Hide 2D Legend",
                        labelPosition="top",
                        vertical=False,
                        value=True,
                    ),
                    # add hide selection toggle
                    daq.ToggleSwitch(
                        id="hide-selections-toggle",
                        size=40,
                        color="#c5040d",
                        label="Hide Selections",
                        labelPosition="top",
                        vertical=False,
                        value=False,
                    ),
                    # add save selection toggle
                    daq.ToggleSwitch(
                        id="save-selections-toggle",
                        size=40,
                        color="#c5040d",
                        label="Store Selections",
                        labelPosition="top",
                        vertical=False,
                        value=False,
                    ),
                    html.P("NOTE"),
                    html.Br(),
                    html.P(
                        "Toggling save with contigs selected will save them as a refinement group."
                    ),
                ],
                className="two columns",
            ),
        ],
    ),
    # 3D-scatter plot row div
    html.Div(
        [
            html.Div(
                [
                    html.Label("Figure 2: 3D Binning Overview"),
                    dcc.Graph(
                        id="scatterplot-3d",
                        clear_on_unhover=True,
                        style={"height": "90%", "width": "98%"},
                        config={
                            "toImageButtonOptions": dict(
                                format="svg",
                                filename="scatter3dPlot.autometa.binning",
                            ),
                        },
                    ),
                ],
                className="seven columns threeD_scatter_div",
            ),
            html.Div(
                [
                    html.Label("Figure 3: Taxon Distribution"),
                    dcc.Graph(
                        id="taxonomy-piechart",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="three columns taxa_chart_div",
            ),
            html.Div(
                [
                    html.Label("Fig. 2: Change Z-axis"),
                    dcc.Dropdown(
                        id="scatterplot-3d-zaxis-dropdown",
                        options=[
                            {"label": "Coverage", "value": "coverage"},
                            {"label": "GC Content", "value": "gc_content"},
                            {"label": "Length", "value": "length"},
                        ],
                        value="coverage",
                        clearable=False,
                    ),
                    # add scatterplot-3d-legend-toggle
                    daq.ToggleSwitch(
                        id="scatterplot-3d-legend-toggle",
                        size=40,
                        color="#c5040d",
                        label="Show/Hide 3D scatterplot Legend",
                        labelPosition="top",
                        vertical=False,
                        value=True,
                    ),
                    html.Label("Fig. 3: Distribute Taxa by Rank"),
                    dcc.Dropdown(
                        id="taxonomy-piechart-dropdown",
                        options=[
                            {"label": "Kingdom", "value": "superkingdom"},
                            {"label": "Phylum", "value": "phylum"},
                            {"label": "Class", "value": "class"},
                            {"label": "Order", "value": "order"},
                            {"label": "Family", "value": "family"},
                            {"label": "Genus", "value": "genus"},
                            {"label": "Species", "value": "species"},
                        ],
                        value="superkingdom",
                        clearable=False,
                    ),
                ],
                className="two columns",
            ),
        ],
        className="row",
        style={"marginTop": "0", "marginBottom": "2"},
    ),
    html.Label("Current Manual Refinement Table"),
    # table div
    html.Div(
        className="row twelve columns binning_table",
        id="refinements-table",
    ),
]


@app.callback(
    Output("color-by-column", "options"), [Input("metagenome-annotations", "children")]
)
def get_color_by_cols(annotations):
    df = pd.read_json(annotations, orient="split")
    return [
        {"label": col.title().replace("_", " "), "value": col}
        for col in df.columns
        if df[col].dtype.name not in {"float64", "int64"} and col != "contig"
    ]


@app.callback(
    Output("selection-binning-metrics", "children"),
    [
        Input("kingdom-markers", "children"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def display_selection_summary(markers, selected_contigs):
    if not selected_contigs:
        num_expected_markers = pd.NA
        num_markers_present = pd.NA
        total_markers = pd.NA
        n_marker_sets = pd.NA
        completeness = pd.NA
        purity = pd.NA
        n_selected = 0
    else:
        df = pd.read_json(markers, orient="split").set_index("contig")
        contigs = {point["text"] for point in selected_contigs["points"]}
        n_selected = len(selected_contigs["points"])
        num_expected_markers = df.shape[1]
        pfam_counts = df.loc[df.index.isin(contigs)].sum()
        if pfam_counts.empty:
            total_markers = 0
            num_single_copy_markers = 0
            num_markers_present = 0
            completeness = pd.NA
            purity = pd.NA
            n_marker_sets = pd.NA
        else:
            total_markers = pfam_counts.sum()
            num_single_copy_markers = pfam_counts.eq(1).count()
            num_markers_present = pfam_counts.ge(1).count()
            completeness = num_markers_present / num_expected_markers * 100
            purity = num_single_copy_markers / num_markers_present * 100
            n_marker_sets = total_markers / num_expected_markers
    # TODO: Create cleaner table for Sam to read completeness/purity etc.
    return f"""
    Selection Binning Metrics:
    -----------------------
|    Markers Expected:\t{num_expected_markers}\t|
|    Unique Markers:\t{num_markers_present}\t|
|    Total Markers:\t{total_markers:,}\t|
|    Marker Set(s):\t{n_marker_sets:.02f}\t|
|    Completeness:\t{completeness:.02f}\t|
|    Purity:\t\t{purity:.02f}\t|
|    Contigs Selected:\t{n_selected:,}\t|
    -----------------------
    """


@app.callback(
    Output("taxonomy-piechart", "figure"),
    [
        Input("metagenome-annotations", "children"),
        Input("scatterplot-2d", "selectedData"),
        Input("taxonomy-piechart-dropdown", "value"),
    ],
)
def taxa_piechart_callback(annotations, selected_contigs, selected_rank):
    df = pd.read_json(annotations, orient="split")
    layout = dict(margin=dict(l=15, r=10, t=35, b=45))
    if not selected_contigs:
        n_ctgs = len(df.index)
        # Get taxa and their respective count at selected canonical-rank
        labels = df[selected_rank].unique().tolist()
        values = [
            len(df[df[selected_rank] == label]) / float(n_ctgs) for label in labels
        ]
        # Add in to pie chart... Sankey (go.Sankey) diagram or Parallel Categories plot (go.ParCat)
        trace = go.Pie(
            labels=labels,
            values=values,
            textinfo="label",
            hoverinfo="label+percent",
            showlegend=False,
        )
        return dict(data=[trace], layout=layout)

    ctg_list = {point["text"] for point in selected_contigs["points"]}
    dff = df[df.contig.isin(ctg_list)]
    n_ctgs = len(dff.index)
    labels = dff[selected_rank].unique().tolist()
    values = [len(dff[dff[selected_rank] == label]) / float(n_ctgs) for label in labels]
    trace = go.Pie(
        labels=labels,
        values=values,
        hoverinfo="label+percent",
        textinfo="label",
        showlegend=False,
    )
    return dict(data=[trace], layout=layout)


@app.callback(
    Output("scatterplot-3d", "figure"),
    [
        Input("metagenome-annotations", "children"),
        Input("scatterplot-3d-zaxis-dropdown", "value"),
        Input("scatterplot-3d-legend-toggle", "value"),
        Input("color-by-column", "value"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def update_zaxis(annotations, zaxis, show_legend, colorby_col, selected_contigs):
    df = pd.read_json(annotations, orient="split")
    titles = {
        "coverage": "Coverage",
        "gc_content": "GC Content",
        "length": "Length",
    }
    zaxis_title = titles[zaxis]
    if not selected_contigs:
        contigs = df.contig.tolist()
    else:
        contigs = {point["text"] for point in selected_contigs["points"]}
    # Subset DataFrame by selected contigs
    df = df[df.contig.isin(contigs)]
    if colorby_col == "cluster":
        # Categoricals for binning
        df[colorby_col] = df[colorby_col].fillna("unclustered")
    else:
        # Other possible categorical columns all relate to taxonomy
        df[colorby_col] = df[colorby_col].fillna("unclassified")
    return {
        "data": [
            go.Scatter3d(
                x=dff.x_1,
                y=dff.x_2,
                z=dff[zaxis],
                text=dff.contig,
                mode="markers",
                textposition="top center",
                opacity=0.45,
                hoverinfo="all",
                marker={
                    "size": dff.assign(normLen=marker_size_scaler)["normLen"].fillna(1),
                    "line": {"width": 0.1, "color": "black"},
                },
                name=colorby_col_value,
            )
            for colorby_col_value, dff in df.groupby(colorby_col)
        ],
        "layout": go.Layout(
            scene=dict(
                xaxis=dict(title="X_1"),
                yaxis=dict(title="X_2"),
                zaxis=dict(title=zaxis_title),
            ),
            legend={"x": 0, "y": 1},
            showlegend=show_legend,
            autosize=True,
            margin=dict(r=0, b=0, l=0, t=25),
            hovermode="closest",
        ),
    }


@app.callback(
    Output("scatterplot-2d", "figure"),
    [
        Input("metagenome-annotations", "children"),
        Input("x-axis-2d", "value"),
        Input("y-axis-2d", "value"),
        Input("show-legend-toggle", "value"),
        Input("color-by-column", "value"),
        Input("refinements-clusters", "children"),
        Input("hide-selections-toggle", "value"),
    ],
)
def update_axes(
    annotations,
    xaxis_column,
    yaxis_column,
    show_legend,
    cluster_col,
    refinement,
    hide_selection_toggle,
):
    df = pd.read_json(annotations, orient="split").set_index("contig")
    titles = {
        "x_1": "X_1",
        "x_2": "X_2",
        "coverage": "Coverage",
        "gc_content": "GC Content",
        "length": "Length",
    }
    xaxis_title = titles[xaxis_column]
    yaxis_title = titles[yaxis_column]
    # Subset metagenome-annotations by selections iff selections have been made
    df[cluster_col] = df[cluster_col].fillna("unclustered")
    if hide_selection_toggle:
        refine_df = pd.read_json(refinement, orient="split").set_index("contig")
        refine_cols = [col for col in refine_df.columns if "refinement" in col]
        if refine_cols:
            refine_col = refine_cols.pop()
            # Retrieve only contigs that have already been refined...
            refined_contigs_index = refine_df[
                refine_df[refine_col].str.contains("refinement")
            ].index
            # print(f"refined df shape: {refine_df.shape}, df shape: {df.shape}")
            df.drop(refined_contigs_index, axis="index", inplace=True, errors="ignore")
            # print(f"new df shape: {df.shape}")
    return {
        "data": [
            go.Scattergl(
                x=df[df[cluster_col] == cluster][xaxis_column],
                y=df[df[cluster_col] == cluster][yaxis_column],
                text=df[df[cluster_col] == cluster].index,
                mode="markers",
                opacity=0.45,
                marker={
                    "size": df.assign(normLen=marker_size_scaler)["normLen"],
                    "line": {"width": 0.1, "color": "black"},
                },
                name=cluster,
            )
            for cluster in df[cluster_col].unique()
        ],
        "layout": go.Layout(
            scene=dict(
                xaxis=dict(title=xaxis_title),
                yaxis=dict(title=yaxis_title),
            ),
            legend={"x": 1, "y": 1},
            showlegend=show_legend,
            margin=dict(r=50, b=50, l=50, t=50),
            # title='2D Clustering Visualization',
            hovermode="closest",
        ),
    }


@app.callback(
    Output("datatable", "data"),
    [
        Input("scatterplot-2d", "selectedData"),
        Input("refinements-clusters", "children"),
    ],
)
def update_table(selected_data, refinements):
    df = pd.read_json(refinements, orient="split")
    if not selected_data:
        return df.to_dict("records")
    contigs = {point["text"] for point in selected_data["points"]}
    return df[df.contig.isin(contigs)].to_dict("records")


@app.callback(
    Output("refinements-table", "children"),
    [Input("refinements-clusters", "children")],
)
def bin_table_callback(df):
    df = pd.read_json(df, orient="split")
    return dash_table.DataTable(
        id="datatable",
        data=df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in df.columns],
        style_cell={"textAlign": "center"},
        style_cell_conditional=[{"if": {"column_id": "contig"}, "textAlign": "right"}],
        virtualization=True,
    )


@app.callback(
    Output("refinements-download", "data"),
    [
        Input("refinements-download-button", "n_clicks"),
        Input("refinements-clusters", "children"),
    ],
)
def download_refinements(n_clicks, intermediate_selections):
    if not n_clicks:
        raise PreventUpdate
    df = pd.read_json(intermediate_selections, orient="split")
    return send_data_frame(df.to_csv, "refinements.csv", index=False)


@app.callback(
    Output("refinements-clusters", "children"),
    [
        Input("scatterplot-2d", "selectedData"),
        Input("refinement-data", "children"),
        Input("save-selections-toggle", "value"),
    ],
    [State("refinements-clusters", "children")],
)
def store_binning_refinement_selections(
    selected_data, refinement_data, save_toggle, intermediate_selections
):
    if not selected_data and not intermediate_selections:
        # We first load in our binning information for refinement
        # Note: this callback should trigger on initial load
        # TODO: Could also remove and construct dataframes from selected contigs
        # Then perform merge when intermediate selections are downloaded.
        bin_df = pd.read_json(refinement_data, orient="split")
        bin_df["cluster"].fillna("unclustered", inplace=True)
        return bin_df.to_json(orient="split")
    if not save_toggle or not selected_data:
        raise PreventUpdate
    contigs = {point["text"] for point in selected_data["points"]}
    pdf = pd.read_json(intermediate_selections, orient="split").set_index("contig")
    refinement_cols = [col for col in pdf.columns if "refinement" in col]
    refinement_num = len(refinement_cols) + 1
    group_name = f"refinement_{refinement_num}"
    pdf.loc[contigs, group_name] = group_name
    pdf = pdf.fillna(axis="columns", method="ffill")
    pdf.reset_index(inplace=True)
    return pdf.to_json(orient="split")
