# -*- coding: utf-8 -*-

import itertools
import logging

from pydantic import Json

numba_logger = logging.getLogger("numba")
numba_logger.setLevel(logging.WARNING)
h5py_logger = logging.getLogger("h5py")
h5py_logger.setLevel(logging.WARNING)

from typing import Dict, List

import pandas as pd
import dash_daq as daq

from dash import dcc, html
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput, RedisStore, Input, Output, State
from plotly import graph_objects as go

import dash_bootstrap_components as dbc
import plotly.io as pio

from automappa.app import app, cache
from automappa.utils.models import SampleTables
from automappa import settings

from automappa.utils.serializers import table_to_db

from automappa.utils.figures import (
    format_axis_title,
    get_scatterplot_2d,
    taxonomy_sankey,
    get_scatterplot_3d,
    metric_boxplot,
)

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
backend = RedisStore(settings.celery.backend_url)

pio.templates.default = "plotly_white"


########################################################################
# COMPONENTS: OFFCANVAS SETTINGS
# ######################################################################


color_by_col_dropdown = [
    html.Label("Contigs colored by:"),
    dcc.Dropdown(
        id="color-by-column",
        options=[],
        value="cluster",
        clearable=False,
    ),
]

# Scatterplot 2D Legend Toggle
scatterplot_2d_legend_toggle = daq.ToggleSwitch(
    id="scatterplot-2d-legend-toggle",
    size=40,
    color="#c5040d",
    label="Legend",
    labelPosition="top",
    vertical=False,
    value=True,
)

# TODO: Link x-axis-2d w/ y-axis-2d
# Combinations of kmer embeddings
# kmer-size [dropdown]
# kmer-norm-method [dropdown]
# kmer-embed-method [dropdown]
# All are filters to main dropdown combinations of kmer axes

kmer_size_dropdown = [
    html.Label("K-mer size:"),
    dcc.Dropdown(
        id="kmer-size-dropdown",
        options=[3, 4, 5],
        value=5,
        clearable=False,
    ),
]

norm_method_dropdown = [
    html.Label("K-mer norm. method:"),
    dcc.Dropdown(
        id="norm-method-dropdown",
        options=["am_clr", "ilr"],
        value="am_clr",
        clearable=False,
    ),
]

scatterplot_2d_axes_dropdown = [
    html.Label("Axes:"),
    dcc.Dropdown(
        id="axes-2d",
        value="coverage|gc_content",
        clearable=False,
    ),
]

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

scatterplot_3d_zaxis_dropdown = [
    html.Label("Z-axis:"),
    dcc.Dropdown(
        id="scatterplot-3d-zaxis-dropdown",
        options=[
            {"label": "Coverage", "value": "coverage"},
            {"label": "GC%", "value": "gc_content"},
            {"label": "Length", "value": "length"},
        ],
        value="length",
        clearable=False,
    ),
]

taxa_rank_dropdown = [
    html.Label("Distribute taxa by rank:"),
    dcc.Dropdown(
        id="taxonomy-distribution-dropdown",
        options=[
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

# Download Refinements Button
binning_refinements_download_button = [
    dbc.Button(
        "Download Refinements",
        id="refinements-download-button",
        n_clicks=0,
        color="primary",
    ),
    dcc.Download(id="refinements-download"),
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
                        dbc.Row(dbc.Col(kmer_size_dropdown)),
                        dbc.Row(dbc.Col(norm_method_dropdown)),
                        dbc.Row(dbc.Col(scatterplot_2d_axes_dropdown)),
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
                dbc.Col(binning_refinements_download_button),
                dbc.Col(binning_refinements_summary_button),
            ]
        ),
    ],
    id="settings-offcanvas",
    title="Settings",
    is_open=False,
    placement="end",
    scrollable=True,
)

########################################################################
# COMPONENTS: Buttons and Toggle
# ######################################################################

refinement_settings_button = dbc.Button("Settings", id="settings-button", n_clicks=0)

mag_refinement_save_button = dbc.Button(
    "Save selection to MAG refinement",
    id="mag-refinement-save-button",
    n_clicks=0,
    disabled=True,
)

# Tooltip for info on store selections behavior
hide_selections_tooltip = dbc.Tooltip(
    'Toggling this to the "on" state will hide your manually-curated MAG refinement groups',
    target="hide-selections-toggle",
    placement="auto",
)

# add hide selection toggle
hide_selections_toggle = daq.ToggleSwitch(
    id="hide-selections-toggle",
    size=40,
    color="#c5040d",
    label="Hide MAG Refinements",
    labelPosition="top",
    vertical=False,
    value=False,
)

# TODO: Refactor to update scatterplot legend with update marker symbol traces...
marker_symbols_label = html.Pre(
    """
Marker Symbol    Circle: 0    Diamond:  2          X: 4    Hexagon: 6
 Count Legend    Square: 1   Triangle:  3   Pentagon: 5   Hexagram: 7+
"""
)

mag_refinement_buttons = html.Div(
    [
        refinement_settings_button,
        refinement_settings_offcanvas,
        mag_refinement_save_button,
        hide_selections_toggle,
        hide_selections_tooltip,
        marker_symbols_label,
    ],
    className="d-grid gap-2 d-md-flex justify-content-md-start",
)

########################################################################
# COMPONENTS: FIGURES AND TABLES
# ######################################################################

# Add metrics as alerts using MIMAG standards
# TODO: Add progress bar to emit MAG curation progress
# See: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/progress
# Color using MIMAG thresholds listed below:
# For current standards see the following links:
# contamination: https://genomicsstandardsconsortium.github.io/mixs/contam_score/
# completeness: https://genomicsstandardsconsortium.github.io/mixs/compl_score/
# (success) alert --> passing thresholds (completeness >= 90%, contamination <= 5%)
# (warning) alert --> within 10% thresholds, e.g. (completeness >=80%, contam. <= 15%)
# (danger)  alert --> failing thresholds (completeness less than 80%, contam. >15%)
# TODO: Add callbacks for updating `color`, `value` and `label` with computed completeness and purity values
completeness_progress = dbc.Progress(id="mag-refinement-completeness-progress")
purity_progress = dbc.Progress(id="mag-refinement-purity-progress")


mag_metrics_table = [
    html.Label("Table 1. MAG Marker Metrics"),
    dcc.Loading(
        id="loading-mag-metrics-datatable",
        children=[html.Div(id="mag-metrics-datatable")],
        type="dot",
        color="#646569",
    ),
]

scatterplot_2d = [
    html.Label("Figure 1: 2D Metagenome Overview"),
    dcc.Loading(
        id="loading-scatterplot-2d",
        children=[
            dcc.Graph(
                id="scatterplot-2d",
                clear_on_unhover=True,
                config={"displayModeBar": True, "displaylogo": False},
            )
        ],
        type="graph",
    ),
]

scatterplot_3d = [
    html.Label("Figure 2: 3D Metagenome Overview"),
    dcc.Loading(
        id="loading-scatterplot-3d",
        children=[
            dcc.Graph(
                id="scatterplot-3d",
                clear_on_unhover=True,
                config={
                    "toImageButtonOptions": dict(
                        format="svg",
                        filename="figure_2_3D_metagenome_overview",
                    ),
                    "displayModeBar": True,
                    "displaylogo": False,
                },
            )
        ],
        type="graph",
    ),
]


taxonomy_figure = [
    html.Label("Figure 3: Taxonomic Distribution"),
    dcc.Loading(
        id="loading-taxonomy-distribution",
        children=[
            dcc.Graph(
                id="taxonomy-distribution",
                config={
                    "displayModeBar": False,
                    "displaylogo": False,
                    "staticPlot": True,
                },
            )
        ],
        type="graph",
    ),
]

mag_refinement_coverage_boxplot = [
    html.Label("Figure 4: MAG Refinement Coverage Boxplot"),
    dcc.Loading(
        id="loading-mag-refinement-coverage-boxplot",
        children=[
            dcc.Graph(
                id="mag-refinement-coverage-boxplot",
                config={"displayModeBar": False, "displaylogo": False},
            )
        ],
        type="dot",
        color="#646569",
    ),
]

mag_refinement_gc_content_boxplot = [
    html.Label("Figure 5: MAG Refinement GC Content Boxplot"),
    dcc.Loading(
        id="loading-mag-refinement-gc-content-boxplot",
        children=[
            dcc.Graph(
                id="mag-refinement-gc-content-boxplot",
                config={"displayModeBar": False, "displaylogo": False},
            )
        ],
        type="dot",
        color="#0479a8",
    ),
]

mag_refinement_length_boxplot = [
    html.Label("Figure 6: MAG Refinement Length Boxplot"),
    dcc.Loading(
        id="loading-mag-refinement-length-boxplot",
        children=[
            dcc.Graph(
                id="mag-refinement-length-boxplot",
                config={"displayModeBar": False, "displaylogo": False},
            )
        ],
        type="dot",
        color="#0479a8",
    ),
]


refinements_table = dcc.Loading(
    id="loading-refinements-table",
    children=[html.Div(id="refinements-table")],
    type="circle",
    color="#646569",
)


########################################################################
# LAYOUT
# ######################################################################

# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
# For best results, make sure you adhere to the following two rules when constructing your layouts:
#
# 1. Only use Row and Col inside a Container.
# 2. The immediate children of any Row component should always be Col components.
# 3. Your content should go inside the Col components.
binning_store = dcc.Loading(dcc.Store("binning-store"), type="dot")

layout = dbc.Container(
    children=[
        binning_store,
        dbc.Row([dbc.Col(mag_refinement_buttons)]),
        dbc.Row(
            [dbc.Col(scatterplot_2d, width=9), dbc.Col(mag_metrics_table, width=3)]
        ),
        # TODO: Add MAG assembly metrics table
        dbc.Row([dbc.Col(taxonomy_figure, width=9), dbc.Col(scatterplot_3d, width=3)]),
        dbc.Row(
            [
                dbc.Col(mag_refinement_coverage_boxplot, width=4),
                dbc.Col(mag_refinement_gc_content_boxplot, width=4),
                dbc.Col(mag_refinement_length_boxplot, width=4),
            ]
        ),
        dbc.Row([dbc.Col(refinements_table, width=12)]),
    ],
    fluid=True,
)


########################################################################
# CALLBACKS
# ######################################################################


# @cache.memoize(timeout=3600)
@app.callback(
    ServersideOutput("binning-store", "data", backend=backend),
    Input("selected-tables-store", "data"),
    memoize=True,
)
def query_binning_in_db(selected_tables_data: SampleTables):
    sample = SampleTables.parse_raw(selected_tables_data)
    return sample.binning.table.reset_index().to_json("records")


@app.callback(
    Output("settings-offcanvas", "is_open"),
    Input("settings-button", "n_clicks"),
    [State("settings-offcanvas", "is_open")],
)
def toggle_offcanvas(n1: int, is_open: bool) -> bool:
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("color-by-column", "options"), Input("selected-tables-store", "data")
)
def color_by_column_options_callback(selected_tables_data: SampleTables):
    sample = SampleTables.parse_raw(selected_tables_data)
    df = sample.binning.table
    return [
        {"label": col.title().replace("_", " "), "value": col}
        for col in df.select_dtypes("object").columns
    ]


@app.callback(
    Output("axes-2d", "options"),
    Input("selected-tables-store", "data"),
    Input("kmer-size-dropdown", "value"),
    Input("norm-method-dropdown", "value"),
)
def axes_2d_options_callback(
    selected_tables_data: Json[SampleTables],
    kmer_size_dropdown_value: int,
    norm_method_dropdown_value: str,
) -> List[Dict[str, str]]:
    sample = SampleTables.parse_raw(selected_tables_data)
    binning_df = sample.binning.table
    binning_combinations = [
        {
            "label": " vs. ".join(
                [x_axis.title().replace("_", " "), y_axis.title().replace("_", " ")]
            ),
            "value": "|".join([x_axis, y_axis]),
            "disabled": False,
        }
        for x_axis, y_axis in itertools.combinations(
            binning_df.select_dtypes({"float64", "int64"}).columns, 2
        )
        if x_axis not in {"completeness", "purity", "taxid"}
        and y_axis not in {"completeness", "purity", "taxid"}
    ]
    embeddings = [
        {
            "label": kmer.embedding.name,
            "value": f"{kmer.embedding.name}_x_1|{kmer.embedding.name}_x_2",
            "disabled": not kmer.embedding.exists,
        }
        for kmer in sample.kmers
        if kmer.size == kmer_size_dropdown_value
        and kmer.norm_method == norm_method_dropdown_value
    ]
    return binning_combinations + embeddings


@app.callback(
    Output("mag-metrics-datatable", "children"),
    [
        Input("selected-tables-store", "data"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def update_mag_metrics_datatable_callback(
    selected_tables_data: Json[SampleTables],
    selected_contigs: Dict[str, List[Dict[str, str]]],
) -> DataTable:
    sample = SampleTables.parse_raw(selected_tables_data)
    markers_df = sample.markers.table
    if selected_contigs:
        contigs = {point["text"] for point in selected_contigs["points"]}
        selected_contigs_count = len(contigs)
        markers_df = markers_df.loc[markers_df.index.isin(contigs)]

    expected_markers_count = markers_df.shape[1]

    pfam_counts = markers_df.sum()
    if pfam_counts[pfam_counts.ge(1)].empty:
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
        selection_metrics = {
            "Contigs": selected_contigs_count,
            "Completeness (%)": completeness,
            "Purity (%)": purity,
        }
        selection_metrics.update(metrics_data)
        # Adding this extra step b/c to keep selection metrics at top of the table...
        metrics_data = selection_metrics

    metrics_df = pd.DataFrame([metrics_data]).T
    metrics_df.rename(columns={0: "Value"}, inplace=True)
    metrics_df.index.name = "MAG Metric"
    metrics_df.reset_index(inplace=True)
    metrics_df = metrics_df.round(2)
    return DataTable(
        data=metrics_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in metrics_df.columns],
        style_cell={
            "height": "auto",
            # all three widths are needed
            "minWidth": "20px",
            "width": "20px",
            "maxWidth": "20px",
            "whiteSpace": "normal",
            "textAlign": "center",
        },
        # TODO: style completeness and purity cells to MIMAG standards as mentioned above
    )


@app.callback(
    Output("scatterplot-2d", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("kmer-size-dropdown", "value"),
        Input("norm-method-dropdown", "value"),
        Input("axes-2d", "value"),
        Input("scatterplot-2d-legend-toggle", "value"),
        Input("color-by-column", "value"),
        Input("hide-selections-toggle", "value"),
        Input("mag-refinement-save-button", "n_clicks"),
    ],
)
def scatterplot_2d_figure_callback(
    # selected_tables_data: MetagenomeAnnotationsTables,
    selected_tables_data: Json[SampleTables],
    kmer_size_dropdown_value: int,
    norm_method_dropdown_value: str,
    axes_columns: str,
    show_legend: bool,
    color_by_col: str,
    hide_selection_toggle: bool,
    btn_clicks: int,
) -> go.Figure:
    # NOTE: btn_clicks is an input so this figure is updated when new refinements are saved
    # TODO: #23 refactor scatterplot callbacks
    # - Add Input("scatterplot-2d", "layout") ?
    # TODO: Refactor data retrieval/validation
    sample = SampleTables.parse_raw(selected_tables_data)
    bin_df = sample.binning.table
    # TODO: Replace binning table w/coords-data
    # Replace binning table w/metagenome-annotations-data[TODO]
    # mag_cols=["length", "gc_content", "coverage"]
    markers = sample.marker_symbols.table
    if color_by_col not in bin_df.columns:
        for col in ["phylum", "class", "order", "family"]:
            if col in bin_df.columns:
                color_by_col = col
                break
    if color_by_col not in bin_df.columns:
        raise ValueError(
            f"No columns were found in binning-main that could be used to group traces. {color_by_col} not found in table..."
        )
    # Subset metagenome-annotations by selections iff selections have been made
    if hide_selection_toggle:
        refine_df = sample.refinements.table
        refine_cols = [col for col in refine_df.columns if "refinement" in col]
        if refine_cols:
            latest_refine_col = refine_cols.pop()
            # Retrieve only contigs that have already been refined...
            refined_contigs_index = refine_df[
                refine_df[latest_refine_col].str.contains("refinement")
            ].index
            bin_df.drop(
                refined_contigs_index, axis="index", inplace=True, errors="ignore"
            )
    # TODO: Refactor figure s.t. updates are applied in
    # batches for respective styling,layout,traces, etc.
    # TODO: Put figure or traces in store, get/update/select
    # based on current contig selections
    # TODO: Should check norm_method, kmer_size prior to retrieving embeddings table...
    # Add norm method and kmer_size dropdowns...
    xaxis_column, yaxis_column = axes_columns.split("|")
    if "_x_1" in xaxis_column or "_x_2" in yaxis_column:
        # TODO: Fix retrieval of axes with embeddings...
        for embeddings in sample.embeddings:
            sizemers, norm_method, __ = embeddings.name.split("-")
            kmer_size = int(sizemers.replace("mers", ""))
            if (
                norm_method == norm_method_dropdown_value
                and kmer_size == kmer_size_dropdown_value
                and embeddings.exists
            ):
                embedding_df = embeddings.table
                bin_df = bin_df.join(embedding_df, how="left")
    else:
        for kmer in sample.kmers:
            if (
                f"{kmer.embedding.name}_x_1" == xaxis_column
                and f"{kmer.embedding.name}_x_2" == yaxis_column
                and kmer.size == kmer_size_dropdown_value
                and kmer.norm_method == norm_method_dropdown_value
            ):
                bin_df = bin_df.join(kmer.embedding.table, how="left")
                break

    fillnas = {
        "cluster": "unclustered",
        "superkingdom": "unclassified",
        "phylum": "unclassified",
        "class": "unclassified",
        "order": "unclassified",
        "family": "unclassified",
        "genus": "unclassified",
        "species": "unclassified",
    }
    fillna = fillnas.get(color_by_col, "unclustered")
    fig = get_scatterplot_2d(
        bin_df,
        x_axis=xaxis_column,
        y_axis=yaxis_column,
        color_by_col=color_by_col,
        fillna=fillna,
    )

    # TODO: If possible, as a separate callback do Output("scatterplot-2d", "layout")
    with fig.batch_update():
        fig.layout.xaxis.title = format_axis_title(xaxis_column)
        fig.layout.yaxis.title = format_axis_title(yaxis_column)
        fig.layout.legend.title = color_by_col.title()
        fig.layout.showlegend = show_legend

    # Update markers with symbol and size corresponding to marker count
    # TODO: If possible, as a separate callback do Output("scatterplot-2d", "traces")
    fig.for_each_trace(
        lambda trace: trace.update(
            marker_symbol=markers.symbol.loc[trace.text],
            marker_size=markers.marker_size.loc[trace.text],
        )
    )
    return fig


@app.callback(
    Output("taxonomy-distribution", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("scatterplot-2d", "selectedData"),
        Input("taxonomy-distribution-dropdown", "value"),
    ],
)
def taxonomy_distribution_figure_callback(
    selected_tables_data: SampleTables,
    selected_contigs: Dict[str, List[Dict[str, str]]],
    selected_rank: str,
) -> go.Figure:
    sample = SampleTables.parse_raw(selected_tables_data)
    df = sample.binning.table
    if selected_contigs and selected_contigs["points"]:
        contigs = {point["text"] for point in selected_contigs["points"]}
        df = df.loc[df.index.isin(contigs)]
    fig = taxonomy_sankey(df, selected_rank=selected_rank)
    return fig


@app.callback(
    Output("scatterplot-3d", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("axes-2d", "value"),
        Input("scatterplot-3d-zaxis-dropdown", "value"),
        Input("scatterplot-3d-legend-toggle", "value"),
        Input("color-by-column", "value"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def scatterplot_3d_figure_callback(
    selected_tables_data: SampleTables,
    axes_columns: str,
    z_axis: str,
    show_legend: bool,
    color_by_col: str,
    selected_contigs: Dict[str, List[Dict[str, str]]],
) -> go.Figure:
    sample = SampleTables.parse_raw(selected_tables_data)
    df = sample.binning.table
    color_by_col = "phylum" if color_by_col not in df.columns else color_by_col
    if not selected_contigs:
        contigs = set(df.index.tolist())
    else:
        contigs = {point["text"] for point in selected_contigs["points"]}
    # Subset DataFrame by selected contigs
    df = df[df.index.isin(contigs)]
    if color_by_col == "cluster":
        # Categoricals for binning
        df[color_by_col] = df[color_by_col].fillna("unclustered")
    else:
        # Other possible categorical columns all relate to taxonomy
        df[color_by_col] = df[color_by_col].fillna("unclassified")

    x_axis, y_axis = axes_columns.split("|")
    fig = get_scatterplot_3d(
        df=df,
        x_axis=x_axis,
        y_axis=y_axis,
        z_axis=z_axis,
        color_by_col=color_by_col,
    )
    fig.update_layout(showlegend=show_legend)
    return fig


@app.callback(
    Output("mag-refinement-coverage-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def mag_summary_coverage_boxplot_callback(
    selected_tables_data: SampleTables, selected_data: Dict[str, List[Dict[str, str]]]
) -> go.Figure:
    if not selected_data:
        raise PreventUpdate
    sample = SampleTables.parse_raw(selected_tables_data)
    df = sample.binning.table
    contigs = {point["text"] for point in selected_data["points"]}
    df = df.loc[df.index.isin(contigs)]
    fig = metric_boxplot(df, metrics=["coverage"], boxmean="sd")
    return fig


@app.callback(
    Output("mag-refinement-gc-content-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def mag_summary_gc_content_boxplot_callback(
    selected_tables_data: SampleTables, selected_data: Dict[str, List[Dict[str, str]]]
) -> go.Figure:
    if not selected_data:
        raise PreventUpdate
    sample = SampleTables.parse_raw(selected_tables_data)
    df = sample.binning.table
    contigs = {point["text"] for point in selected_data["points"]}
    df = df.loc[df.index.isin(contigs)]
    fig = metric_boxplot(df, metrics=["gc_content"], boxmean="sd")
    fig.update_traces(name="GC Content")
    return fig


@app.callback(
    Output("mag-refinement-length-boxplot", "figure"),
    [
        Input("selected-tables-store", "data"),
        Input("scatterplot-2d", "selectedData"),
    ],
)
def mag_summary_length_boxplot_callback(
    selected_tables_data: SampleTables, selected_data: Dict[str, List[Dict[str, str]]]
) -> go.Figure:
    if not selected_data:
        raise PreventUpdate
    sample = SampleTables.parse_raw(selected_tables_data)
    df = sample.binning.table
    contigs = {point["text"] for point in selected_data["points"]}
    df = df.loc[df.index.isin(contigs)]
    fig = metric_boxplot(df, metrics=["length"])
    return fig


@app.callback(
    Output("refinements-table", "children"),
    [
        Input("selected-tables-store", "data"),
        Input("mag-refinement-save-button", "n_clicks"),
    ],
)
def refinements_table_callback(
    selected_tables_data: SampleTables,
    btn_clicks: int,
) -> DataTable:
    sample = SampleTables.parse_raw(selected_tables_data)
    return DataTable(
        data=sample.refinements.table.to_dict("records"),
        columns=[{"name": col, "id": col} for col in sample.refinements.table.columns],
        style_cell={"textAlign": "center"},
        style_cell_conditional=[{"if": {"column_id": "contig"}, "textAlign": "right"}],
        virtualization=True,
    )


@app.callback(
    Output("refinements-download", "data"),
    [
        Input("refinements-download-button", "n_clicks"),
        Input("selected-tables-store", "data"),
    ],
)
def download_refinements(
    n_clicks: int,
    selected_tables_data: SampleTables,
) -> Dict[str, "str | bool"]:
    if not n_clicks:
        raise PreventUpdate
    sample = SampleTables.parse_raw(selected_tables_data)
    return dcc.send_data_frame(
        sample.refinements.table.to_csv, "refinements.csv", index=False
    )


@app.callback(
    Output("mag-refinement-save-button", "disabled"),
    [Input("scatterplot-2d", "selectedData")],
)
def mag_refinement_save_button_disabled_callback(
    selected_data: Dict[str, List[Dict[str, str]]]
) -> bool:
    return not selected_data


@app.callback(
    Output("mag-refinement-save-button", "n_clicks"),
    [
        Input("scatterplot-2d", "selectedData"),
        Input("selected-tables-store", "data"),
        Input("mag-refinement-save-button", "n_clicks"),
    ],
)
def store_binning_refinement_selections(
    selected_data: Dict[str, List[Dict[str, str]]],
    selected_tables_data: SampleTables,
    n_clicks: int,
) -> int:
    # Initial load...
    if not n_clicks or (n_clicks and not selected_data) or not selected_data:
        raise PreventUpdate
    sample = SampleTables.parse_raw(selected_tables_data)
    bin_df = sample.refinements.table
    refinement_cols = [col for col in bin_df.columns if "refinement" in col]
    refinement_num = len(refinement_cols) + 1
    refinement_name = f"refinement_{refinement_num}"
    contigs = list({point["text"] for point in selected_data["points"]})
    bin_df.loc[contigs, refinement_name] = refinement_name
    bin_df = bin_df.fillna(axis="columns", method="ffill")
    bin_df.reset_index(inplace=True)
    table_to_db(df=bin_df, name=sample.refinements.id)
    return 0
