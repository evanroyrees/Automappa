# -*- coding: utf-8 -*-

from typing import Dict, List
import pandas as pd
import dash_daq as daq
from dash import dcc, html
from dash.dash_table import DataTable
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import dash_bootstrap_components as dbc
from app import app
from plotly import graph_objects as go
import numpy as np


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


########################################################################
# HIDDEN DIV to store refinement information
# ######################################################################

refinements_clusters_store = (
    dcc.Store(id="refinements-clusters-store", storage_type="session"),
)

########################################################################
# COMPONENTS: OFFCANVAS SETTINGS
# ######################################################################


color_by_col_dropdown = dbc.Row(
    children=[
        html.Label("Contigs colored by:"),
        dcc.Dropdown(
            id="color-by-column",
            options=[],
            value="cluster",
            clearable=False,
        ),
    ],
)

scatterplot_2d_xaxis_dropdown = dbc.Row(
    children=[
        html.Label("X-axis:"),
        dcc.Dropdown(
            id="x-axis-2d",
            options=[
                {"label": "X_1", "value": "x_1"},
                {"label": "Coverage", "value": "coverage"},
                {"label": "GC%", "value": "gc_content"},
                {"label": "Length", "value": "length"},
            ],
            value="x_1",
            clearable=False,
        ),
    ],
)

scatterplot_2d_yaxis_dropdown = dbc.Row(
    children=[
        html.Label("Y-axis:"),
        dcc.Dropdown(
            id="y-axis-2d",
            options=[
                {"label": "X_2", "value": "x_2"},
                {"label": "Coverage", "value": "coverage"},
                {"label": "GC%", "value": "gc_content"},
                {"label": "Length", "value": "length"},
            ],
            value="x_2",
            clearable=False,
        ),
    ],
)

scatterplot_3d_zaxis_dropdown = dbc.Row(
    children=[
        html.Label("Z-axis:"),
        dcc.Dropdown(
            id="scatterplot-3d-zaxis-dropdown",
            options=[
                {"label": "Coverage", "value": "coverage"},
                {"label": "GC%", "value": "gc_content"},
                {"label": "Length", "value": "length"},
            ],
            value="coverage",
            clearable=False,
        ),
    ]
)

taxa_rank_dropdown = dbc.Row(
    children=[
        html.Label("Distribute taxa by rank:"),
        dcc.Dropdown(
            id="taxonomy-distribution-dropdown",
            options=[
                {"label": "Kingdom", "value": "superkingdom"},
                {"label": "Phylum", "value": "phylum"},
                {"label": "Class", "value": "class"},
                {"label": "Order", "value": "order"},
                {"label": "Family", "value": "family"},
                {"label": "Genus", "value": "genus"},
                {"label": "Species", "value": "species"},
            ],
            value="species",
            clearable=False,
        ),
    ]
)

# add show-legend-toggle
scatterplot_2d_legend_toggle = daq.ToggleSwitch(
    id="show-legend-toggle",
    size=40,
    color="#c5040d",
    label="Legend",
    labelPosition="top",
    vertical=False,
    value=True,
)

# Tooltip for info on store selections behavior
hide_selections_tooltip = dbc.Tooltip(
    'Toggling this to the "on" state will hide your manually-curated MAG refinement groups',
    target="hide-selections-toggle",
    placement="left",
)

# add hide selection toggle
hide_selections_toggle = daq.ToggleSwitch(
    id="hide-selections-toggle",
    size=40,
    color="#c5040d",
    label="Hide MAG Refinements",
    labelPosition="left",
    vertical=False,
    value=False,
)

# Tooltip for info on store selections behavior
save_selections_tooltip = dbc.Tooltip(
    """Toggling this to the \"on\" state while selecting contigs (or while contigs are selected)
    will save the selected contigs to their own MAG refinement group
    """,
    target="save-selections-toggle",
    placement="left",
)

# add save selection toggle
save_selections_toggle = daq.ToggleSwitch(
    id="save-selections-toggle",
    size=40,
    color="#c5040d",
    label="Select MAG Refinements",
    labelPosition="left",
    vertical=False,
    value=False,
)

# Scatterplot 3D Legend Toggle
scatterplot_3d_legend_toggle = daq.ToggleSwitch(
    id="scatterplot-3d-legend-toggle",
    size=40,
    color="#c5040d",
    label="Legend",
    labelPosition="top",
    vertical=False,
    value=True,
)

# Download Refinements Button
binning_refinements_download_button = [
    dbc.Button(
        "Download Refinements",
        id="refinements-download-button",
        n_clicks=0,
        color="primary",
    ),
    Download(id="refinements-download"),
]

# Summarize Refinements Button
binning_refinements_summary_button = [
    dbc.Button(
        "Summarize Refinements",
        id="refinements-summary-button",
        n_clicks=0,
        color="primary",
    ),
]


refinement_settings_offcanvas = dbc.Offcanvas(
    [
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dbc.Row(
                            [
                                dbc.Col(color_by_col_dropdown),
                                dbc.Col(scatterplot_2d_legend_toggle),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(scatterplot_2d_xaxis_dropdown),
                                dbc.Col(scatterplot_2d_yaxis_dropdown),
                            ]
                        ),
                    ],
                    title="Figure 1: 2D Metagenome Overview",
                ),
                dbc.AccordionItem(
                    [
                        dbc.Row(
                            [
                                dbc.Col(scatterplot_3d_zaxis_dropdown),
                                dbc.Col(scatterplot_3d_legend_toggle),
                            ]
                        ),
                    ],
                    title="Figure 2: 3D Metagenome Overview",
                ),
                dbc.AccordionItem(
                    [
                        dbc.Col(taxa_rank_dropdown),
                    ],
                    title="Figure 3: Taxonomic Distribution",
                ),
            ],
            start_collapsed=True,
            flush=True,
        ),
        dbc.Row(
            [
                dbc.Col([save_selections_tooltip, save_selections_toggle]),
                dbc.Col([hide_selections_tooltip, hide_selections_toggle]),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(binning_refinements_download_button),
                dbc.Col(binning_refinements_summary_button),
            ]
        ),
    ],
    id="refinement-settings-offcanvas",
    title="Refinement Settings",
    is_open=False,
    placement="end",
    scrollable=True,
)

refinement_settings_button = [
    dbc.Button("Refinement Settings", id="refinement-settings-button", n_clicks=0),
    refinement_settings_offcanvas,
]

########################################################################
# COMPONENTS: FIGURES AND TABLES
# ######################################################################

# Add metrics as alerts using MIMAG standards
# (success) alert --> passing thresholds (completeness >= 90%, contamination <= 5%)
# (warning) alert --> within 10% thresholds, e.g. (completeness >=80%, contam. <= 15%)
# (danger)  alert --> failing thresholds (completeness less than 80%, contam. >15%)

mag_metrics_table = html.Div(id="mag-metrics-datatable")

scatterplot_2d = [
    html.Label("Figure 1: 2D Metagenome Overview"),
    dcc.Graph(
        id="scatterplot-2d",
        clear_on_unhover=True,
    ),
]

scatterplot_3d = [
    html.Label("Figure 2: 3D Metagenome Overview"),
    dcc.Graph(
        id="scatterplot-3d",
        clear_on_unhover=True,
        config={
            "toImageButtonOptions": dict(
                format="svg",
                filename="scatter3dPlot.autometa.binning",
            ),
        },
    ),
]


taxonomy_figure = [
    html.Label("Figure 3: Taxonomic Distribution"),
    dcc.Graph(id="taxonomy-distribution"),
]

refinements_table = html.Div(id="refinements-table")


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
    children=[
        dbc.Col(refinements_clusters_store),
        dbc.Col(refinement_settings_button, width=12),
        dbc.Row([dbc.Col(mag_metrics_table, width=4), dbc.Col(scatterplot_2d)]),
        dbc.Row([dbc.Col(scatterplot_3d), dbc.Col(taxonomy_figure)]),
        dbc.Row(dbc.Col(refinements_table, width=12)),
    ],
    fluid=True,
)


########################################################################
# CALLBACKS
# ######################################################################


@app.callback(
    Output("refinement-settings-offcanvas", "is_open"),
    Input("refinement-settings-button", "n_clicks"),
    [State("refinement-settings-offcanvas", "is_open")],
)
def toggle_offcanvas(n1: int, is_open: bool) -> bool:
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("color-by-column", "options"), [Input("metagenome-annotations", "children")]
)
def color_by_column_options_callback(annotations_json: "str | None"):
    df = pd.read_json(annotations_json, orient="split")
    return [
        {"label": col.title().replace("_", " "), "value": col}
        for col in df.columns
        if df[col].dtype.name not in {"float64", "int64"} and col != "contig"
    ]


@app.callback(
    Output("mag-metrics-datatable", "children"),
    [
        Input("kingdom-markers", "children"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def update_mag_metrics_datatable_callback(
    markers_json: "str | None", selected_contigs: Dict[str, List[Dict[str, str]]]
) -> DataTable:
    markers_df = pd.read_json(markers_json, orient="split").set_index("contig")
    if selected_contigs:
        contigs = {point["text"] for point in selected_contigs["points"]}
        selected_contigs_count = len(contigs)
        markers_df = markers_df.loc[markers_df.index.isin(contigs)]

    expected_markers_count = markers_df.shape[1]

    pfam_counts = markers_df.sum()
    if pfam_counts.empty:
        total_markers = 0
        single_copy_marker_count = 0
        markers_present_count = 0
        redundant_markers_count = 0
        marker_set_count = 0
        completeness = "NA"
        purity = "NA"
    else:
        total_markers = pfam_counts.sum()
        single_copy_marker_count = pfam_counts.eq(1).sum()
        markers_present_count = pfam_counts.ge(1).sum()
        redundant_markers_count = pfam_counts.gt(1).sum()
        completeness = markers_present_count / expected_markers_count * 100
        purity = single_copy_marker_count / markers_present_count * 100
        marker_set_count = total_markers / expected_markers_count

    marker_contig_count = markers_df.sum(axis=1).ge(1).sum()
    single_marker_contig_count = markers_df.sum(axis=1).eq(1).sum()
    multi_marker_contig_count = markers_df.sum(axis=1).gt(1).sum()
    metrics_data = {
        "Expected Markers": expected_markers_count,
        "Total Markers": total_markers,
        "Redundant-Markers": redundant_markers_count,
        "Markers Count": markers_present_count,
        "Marker Sets (Total / Expected)": marker_set_count,
        "Marker-Containing Contigs": marker_contig_count,
        "Multi-Marker Contigs": multi_marker_contig_count,
        "Single-Marker Contigs": single_marker_contig_count,
    }
    if selected_contigs:
        metrics_data.update(
            {
                "Contigs": selected_contigs_count,
                "Completeness (%)": completeness,
                "Purity (%)": purity,
            }
        )

    metrics_df = pd.DataFrame([metrics_data]).T
    metrics_df.rename(columns={0: "Value"}, inplace=True)
    metrics_df.index.name = "MAG Metric"
    metrics_df.reset_index(inplace=True)
    metrics_df = metrics_df.round(2)
    return DataTable(
        data=metrics_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in metrics_df.columns],
        style_cell={"textAlign": "center"},
        # TODO: style completeness and purity cells to MIMAG standards as mentioned above
        style_cell_conditional=[{"if": {"column_id": "contig"}, "textAlign": "right"}],
    )


@app.callback(
    Output("taxonomy-distribution", "figure"),
    [
        Input("metagenome-annotations", "children"),
        Input("scatterplot-2d", "selectedData"),
        Input("taxonomy-distribution-dropdown", "value"),
    ],
)
def taxonomy_distribution_figure_callback(
    annotations: "str | None",
    selected_contigs: Dict[str, List[Dict[str, str]]],
    selected_rank: str,
) -> go.Figure:
    df = pd.read_json(annotations, orient="split")
    if selected_contigs:
        ctg_list = {point["text"] for point in selected_contigs["points"]}
        df = df[df.contig.isin(ctg_list)]
    ranks = ["superkingdom", "phylum", "class", "order", "family", "genus", "species"]
    n_ranks = len(ranks[: ranks.index(selected_rank)])
    dff = df[[col for col in df.columns if col in ranks]].fillna("unclassified")
    for rank in ranks:
        if rank in dff:
            dff[rank] = dff[rank].map(
                lambda x: f"{rank[0]}_{x}" if rank != "superkingdom" else f"d_{x}"
            )
    label = []
    for rank in ranks[:n_ranks]:
        label.extend(dff[rank].unique().tolist())
    source = []
    target = []
    value = []
    for rank in ranks[:n_ranks]:
        for rank_name, rank_df in dff.groupby(rank):
            source_index = label.index(rank_name)
            next_rank_i = ranks.index(rank) + 1
            if next_rank_i >= len(ranks[:n_ranks]):
                continue
            next_rank = ranks[next_rank_i]
            # all source is from label rank name index
            for rank_n in rank_df[next_rank].unique():
                target_index = label.index(rank_n)
                value_count = len(rank_df[rank_df[next_rank] == rank_n])
                label.append(source_index)
                source.append(source_index)
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
    Output("scatterplot-3d", "figure"),
    [
        Input("metagenome-annotations", "children"),
        Input("scatterplot-3d-zaxis-dropdown", "value"),
        Input("scatterplot-3d-legend-toggle", "value"),
        Input("color-by-column", "value"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def scatterplot_3d_figure_callback(
    annotations: "str | None",
    zaxis: str,
    show_legend: bool,
    color_by_col: str,
    selected_contigs: Dict[str, List[Dict[str, str]]],
) -> go.Figure:
    df = pd.read_json(annotations, orient="split")
    color_by_col = "phylum" if color_by_col not in df.columns else color_by_col
    if not selected_contigs:
        contigs = df.contig.tolist()
    else:
        contigs = {point["text"] for point in selected_contigs["points"]}
    # Subset DataFrame by selected contigs
    df = df[df.contig.isin(contigs)]
    if color_by_col == "cluster":
        # Categoricals for binning
        df[color_by_col] = df[color_by_col].fillna("unclustered")
    else:
        # Other possible categorical columns all relate to taxonomy
        df[color_by_col] = df[color_by_col].fillna("unclassified")
    return go.Figure(
        data=[
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
            for colorby_col_value, dff in df.groupby(color_by_col)
        ],
        layout=go.Layout(
            scene=dict(
                xaxis=dict(title="X_1"),
                yaxis=dict(title="X_2"),
                zaxis=dict(title=zaxis.replace("_", " ").title()),
            ),
            legend={"x": 0, "y": 1},
            showlegend=show_legend,
            autosize=True,
            margin=dict(r=0, b=0, l=0, t=25),
            hovermode="closest",
        ),
    )


@app.callback(
    Output("scatterplot-2d", "figure"),
    [
        Input("metagenome-annotations", "children"),
        Input("refinements-clusters-store", "data"),
        Input("x-axis-2d", "value"),
        Input("y-axis-2d", "value"),
        Input("show-legend-toggle", "value"),
        Input("color-by-column", "value"),
        Input("hide-selections-toggle", "value"),
    ],
)
def scatterplot_2d_figure_callback(
    annotations: "str | None",
    refinement: "str | None",
    xaxis_column: str,
    yaxis_column: str,
    show_legend: bool,
    color_by_col: str,
    hide_selection_toggle: bool,
) -> go.Figure:
    df = pd.read_json(annotations, orient="split").set_index("contig")
    color_by_col = "phylum" if color_by_col not in df.columns else color_by_col
    # Subset metagenome-annotations by selections iff selections have been made
    df[color_by_col] = df[color_by_col].fillna("unclustered")
    if hide_selection_toggle:
        refine_df = pd.read_json(refinement, orient="split").set_index("contig")
        refine_cols = [col for col in refine_df.columns if "refinement" in col]
        if refine_cols:
            refine_col = refine_cols.pop()
            # Retrieve only contigs that have already been refined...
            refined_contigs_index = refine_df[
                refine_df[refine_col].str.contains("refinement")
            ].index
            df.drop(refined_contigs_index, axis="index", inplace=True, errors="ignore")
    return go.Figure(
        data=[
            go.Scattergl(
                x=df.loc[df[color_by_col].eq(color_col_name), xaxis_column],
                y=df.loc[df[color_by_col].eq(color_col_name), yaxis_column],
                text=df.loc[df[color_by_col].eq(color_col_name)].index,
                mode="markers",
                opacity=0.45,
                marker={
                    "size": df.assign(normLen=marker_size_scaler)["normLen"],
                    "line": {"width": 0.1, "color": "black"},
                },
                name=color_col_name,
            )
            for color_col_name in df[color_by_col].unique()
        ],
        layout=go.Layout(
            scene=dict(
                xaxis=dict(title=xaxis_column.title()),
                yaxis=dict(title=yaxis_column.title()),
            ),
            legend={"x": 1, "y": 1},
            showlegend=show_legend,
            margin=dict(r=50, b=50, l=50, t=50),
            hovermode="closest",
        ),
    )


@app.callback(
    Output("refinements-table", "children"),
    [Input("refinements-clusters-store", "data")],
)
def refinements_table_callback(df: "str | None") -> DataTable:
    df = pd.read_json(df, orient="split")
    return DataTable(
        id="refinements-datatable",
        data=df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in df.columns],
        style_cell={"textAlign": "center"},
        style_cell_conditional=[{"if": {"column_id": "contig"}, "textAlign": "right"}],
        virtualization=True,
    )


@app.callback(
    Output("refinements-datatable", "data"),
    [
        Input("scatterplot-2d", "selectedData"),
        Input("refinements-clusters-store", "data"),
    ],
)
def update_refinements_table(
    selected_data: Dict[str, List[Dict[str, str]]], refinements: "str | None"
) -> "str | None":
    df = pd.read_json(refinements, orient="split")
    if not selected_data:
        return df.to_dict("records")
    contigs = {point["text"] for point in selected_data["points"]}
    return df[df.contig.isin(contigs)].to_dict("records")


@app.callback(
    Output("refinements-download", "data"),
    [
        Input("refinements-download-button", "n_clicks"),
        Input("refinements-clusters-store", "data"),
    ],
)
def download_refinements(
    n_clicks: int, curated_mags: "str | None"
) -> Dict[str, "str | bool"]:
    if not n_clicks:
        raise PreventUpdate
    df = pd.read_json(curated_mags, orient="split")
    return send_data_frame(df.to_csv, "refinements.csv", index=False)


@app.callback(
    Output("refinements-clusters-store", "data"),
    [
        Input("scatterplot-2d", "selectedData"),
        Input("refinement-data", "children"),
        Input("save-selections-toggle", "value"),
    ],
    [State("refinements-clusters-store", "data")],
)
def store_binning_refinement_selections(
    selected_data: Dict[str, List[Dict[str, str]]],
    refinement_data: "str | None",
    save_toggle: bool,
    intermediate_selections: "str | None",
) -> "str | None":
    if not selected_data and not intermediate_selections:
        # We first load in our binning information for refinement
        # Note: this callback should trigger on initial load
        # TODO: Could also remove and construct dataframes from selected contigs
        # Then perform merge when intermediate selections are downloaded.
        bin_df = pd.read_json(refinement_data, orient="split")
        if "cluster" not in bin_df.columns:
            bin_df["cluster"] = "unclustered"
        else:
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
