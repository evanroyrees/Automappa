# -*- coding: utf-8 -*-

import logging
from dash import html, dcc
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.io as pio

import dash_uploader as du

from automappa.app import app
from automappa.tasks import (
    preprocess_clusters_geom_medians,
    preprocess_embeddings,
    preprocess_marker_symbols,
)
from automappa.utils.models import SampleTables
from automappa.utils.serializers import (
    get_uploaded_files_table,
    file_to_db,
    validate_uploader,
)

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)

pio.templates.default = "plotly_white"

########################################################################
# LAYOUT
# ######################################################################

# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
# For best results, make sure you adhere to the following two rules when constructing your layouts:
#
# 1. Only use Row and Col inside a Container.
# 2. The immediate children of any Row component should always be Col components.
# 3. Your content should go inside the Col components.


# dbc.Card() NOTE: Titles, text and links
# Use the 'card-title', 'card-subtitle', and 'card-text' classes to add margins
# and spacing that have been optimized for cards to titles, subtitles and
# text respectively.

binning_main_upload = du.Upload(
    id="upload-binning-main-data",
    text="Drag and Drop or Select binning-main file",
    default_style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    max_files=1,
    # 10240 MB = 10GB
    max_file_size=10240,
)

markers_upload = du.Upload(
    id="upload-markers-data",
    text="Drag and Drop or Select marker annotations file",
    default_style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    max_files=1,
    # 10240 MB = 10GB
    max_file_size=10240,
)

metagenome_upload = du.Upload(
    id="upload-metagenome-data",
    text="Drag and Drop or Select metagenome assembly",
    default_style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    max_files=1,
    # 10240 MB = 10GB
    max_file_size=10240,
)

upload_modal = html.Div(
    [
        dbc.Button("Upload data", id="open-dismiss"),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Upload Metagenome annotations"), close_button=False
                ),
                dbc.ModalBody(
                    [
                        binning_main_upload,
                        markers_upload,
                        metagenome_upload,
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-dismiss", style={"textAlign": "center"}
                    )
                ),
            ],
            id="modal-dismiss",
            keyboard=False,
            backdrop="static",
            fullscreen=True,
        ),
    ],
)

example_card = dbc.Card(
    [
        dbc.CardHeader(id="binning-main-samples-cardheader"),
        dbc.CardBody(
            [
                html.H4("{Filename}", className="card-title"),
                html.H6("Last Updated: {timestamp}", className="card-subtitle"),
                html.Br(),
                html.Ul(
                    [
                        html.Li("Uploaded: {timestamp}", className="card-text"),
                        html.Li("Checksum: {md5sum}", className="card-text"),
                    ]
                ),
                html.Hr(),
                html.H4("Autometa", className="card-subtitle"),
                html.Ul(
                    [
                        html.Li("lengths - (done)"),
                        html.Li("gc-content - (done)"),
                        html.Li("coverage - (done)"),
                        html.Li("markers - (in progress)"),
                        html.Li("taxonomy - (in progress)"),
                        html.Li("kmers -  (queued)"),
                        html.Li("binning - (queued)"),
                        html.Li("binning-summary - (queued)"),
                        html.Li("CheckM - (queued)"),
                        html.Li("GTDB-Tk - (queued)"),
                        html.Li("AntiSMASH - (queued)"),
                    ],
                    className="card-text",
                ),
                html.Div(
                    [
                        dbc.Button("Refine MAGs"),
                        dbc.Button("MAG Summary"),
                    ],
                    className="d-grid gap-2 d-md-flex justify-content-md-center",
                ),
            ]
        ),
        dbc.CardFooter("Processing Status: {status}"),
    ]
)

card_widths = 3
row_example_cards = dbc.Row(
    [
        dbc.Col(example_card, width=card_widths),
    ]
)

samples_datatable = (
    dcc.Loading(
        id="loading-samples-datatable",
        children=[html.Label("Uploaded Datasets"), html.Div(id="samples-datatable")],
        type="dot",
        color="#646569",
    ),
)

selected_tables_datatable = (
    dcc.Loading(
        id="loading-selected-tables-datatable",
        children=[
            html.Label("Selected Datasets for Refinement & Summary:"),
            html.Div(id="selected-tables-datatable"),
        ],
        type="dot",
        color="#646569",
    ),
)

refine_mags_input_groups = html.Div(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Binning"),
                dbc.Select(
                    id="binning-select",
                    placeholder="Select binning annotations",
                ),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Markers"),
                dbc.Select(
                    id="markers-select",
                    placeholder="Select marker annotations",
                ),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Metagenome"),
                dbc.Select(
                    id="metagenome-select",
                    placeholder="Select metagenome annotations",
                ),
            ]
        ),
    ]
)

refine_mags_button = dbc.Button(
    id="refine-mags-button",
    children="Refine MAGs",
)

kmer_embed_tasks_button = dbc.Button(
    id="kmer-embed-tasks-button",
    children="Submit k-mer embedding tasks",
)

tasks_table = html.Div(id="embedding-tasks")

layout = dbc.Container(
    children=[
        dbc.Row(upload_modal),
        html.Br(),
        # row_example_cards,
        dbc.Row(samples_datatable),
        html.Br(),
        dbc.Row(refine_mags_input_groups),
        html.Br(),
        dbc.Row(refine_mags_button),
        html.Br(),
        dbc.Row(selected_tables_datatable),
        html.Br(),
        kmer_embed_tasks_button,
        dbc.Row(tasks_table),
    ],
    fluid=True,
)


@app.callback(
    Output("samples-store", "data"),
    [
        Input("binning-main-upload-store", "modified_timestamp"),
        Input("markers-upload-store", "modified_timestamp"),
        Input("metagenome-upload-store", "modified_timestamp"),
    ],
    [
        State("binning-main-upload-store", "data"),
        State("markers-upload-store", "data"),
        State("metagenome-upload-store", "data"),
        State("samples-store", "data"),
    ],
)
def on_upload_stores_data(
    binning_uploads_timestamp,
    markers_uploads_timestamp,
    metagenome_uploads_timestamp,
    binning_uploads,
    markers_uploads,
    metagenome_uploads,
    samples_store_data,
):
    if (
        binning_uploads is None
        and markers_uploads is None
        and metagenome_uploads is None
    ) or (
        binning_uploads_timestamp is None
        and markers_uploads_timestamp is None
        and metagenome_uploads_timestamp is None
    ):
        # Check if db has any samples in table
        uploaded_files_df = get_uploaded_files_table()
        if not uploaded_files_df.empty:
            return uploaded_files_df.to_json(orient="split")
        raise PreventUpdate
    samples = []
    for data_upload in [
        binning_uploads,
        markers_uploads,
        metagenome_uploads,
        samples_store_data,
    ]:
        df = (
            pd.read_json(data_upload, orient="split") if data_upload else pd.DataFrame()
        )
        samples.append(df)
    samples_df = pd.concat(samples).drop_duplicates(subset=["table_id"])

    logger.debug(f"{samples_df.shape[0]:,} samples retrieved from data upload stores")

    return samples_df.to_json(orient="split")


@app.callback(
    Output("binning-select", "options"),
    [Input("samples-store", "data")],
    State("samples-store", "data"),
)
def binning_select_options(samples_store_data, new_samples_store_data):
    if samples_store_data is None:
        raise PreventUpdate
    samples_df = pd.read_json(samples_store_data, orient="split")
    if new_samples_store_data is not None:
        new_samples_df = pd.read_json(new_samples_store_data, orient="split")
        samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(
            subset=["table_id"]
        )

    if samples_df.empty:
        raise PreventUpdate

    df = samples_df.loc[samples_df.filetype.eq("binning")]
    logger.debug(f"{df.shape[0]:,} binning available for mag_refinement")
    return [
        {
            "label": filename,
            "value": table_id,
        }
        for filename, table_id in zip(df.filename.tolist(), df.table_id.tolist())
    ]


@app.callback(
    Output("markers-select", "options"),
    [Input("samples-store", "data")],
    State("samples-store", "data"),
)
def markers_select_options(samples_store_data, new_samples_store_data):
    if samples_store_data is None:
        raise PreventUpdate
    samples_df = pd.read_json(samples_store_data, orient="split")
    if new_samples_store_data is not None:
        new_samples_df = pd.read_json(new_samples_store_data, orient="split")
        samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(
            subset=["table_id"]
        )

    if samples_df.empty:
        raise PreventUpdate

    markers_samples = samples_df.loc[samples_df.filetype.eq("markers")]
    logger.debug(f"{markers_samples.shape[0]:,} markers available for mag_refinement")
    return [
        {
            "label": filename,
            "value": table_id,
        }
        for filename, table_id in zip(
            markers_samples.filename.tolist(), markers_samples.table_id.tolist()
        )
    ]


@app.callback(
    Output("metagenome-select", "options"),
    [Input("samples-store", "data")],
    State("samples-store", "data"),
)
def metagenome_select_options(samples_store_data, new_samples_store_data):
    if samples_store_data is None:
        raise PreventUpdate
    samples_df = pd.read_json(samples_store_data, orient="split")
    if new_samples_store_data is not None:
        new_samples_df = pd.read_json(new_samples_store_data, orient="split")
        samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(
            subset=["table_id"]
        )

    if samples_df.empty:
        raise PreventUpdate

    df = samples_df.loc[samples_df.filetype.eq("metagenome")]
    logger.debug(f"{df.shape[0]:,} metagenomes available for mag_refinement")
    return [
        {
            "label": filename,
            "value": table_id,
        }
        for filename, table_id in zip(df.filename.tolist(), df.table_id.tolist())
    ]


@app.callback(
    Output("samples-datatable", "children"),
    [Input("samples-store", "data")],
    State("samples-store", "data"),
)
def on_samples_store_data(samples_store_data, new_samples_store_data):
    if samples_store_data is None:
        raise PreventUpdate
    samples_df = pd.read_json(samples_store_data, orient="split")
    if new_samples_store_data is not None:
        new_samples_df = pd.read_json(new_samples_store_data, orient="split")
        samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(
            subset=["table_id"]
        )

    logger.debug(f"retrieved {samples_df.shape[0]:,} samples from samples store")

    if samples_df.empty:
        raise PreventUpdate

    return DataTable(
        data=samples_df.to_dict("records"),
        columns=[
            {"id": col, "name": col, "editable": False} for col in samples_df.columns
        ],
    )


@app.callback(
    Output("binning-main-upload-store", "data"),
    [Input("upload-binning-main-data", "isCompleted")],
    [
        State("upload-binning-main-data", "fileNames"),
        State("upload-binning-main-data", "upload_id"),
    ],
)
def on_binning_main_upload(iscompleted, filenames, upload_id):
    try:
        filepath = validate_uploader(iscompleted, filenames, upload_id)
    except ValueError as err:
        logger.warn(err)
        raise PreventUpdate
    if not filepath:
        raise PreventUpdate
    df = file_to_db(
        filepath=filepath,
        filetype="binning",
    )
    return df.to_json(orient="split")


@app.callback(
    Output("markers-upload-store", "data"),
    [Input("upload-markers-data", "isCompleted")],
    [
        State("upload-markers-data", "fileNames"),
        State("upload-markers-data", "upload_id"),
    ],
)
def on_markers_upload(iscompleted, filenames, upload_id):
    try:
        filepath = validate_uploader(iscompleted, filenames, upload_id)
    except ValueError as err:
        logger.warn(err)
        raise PreventUpdate
    if not filepath:
        raise PreventUpdate
    df = file_to_db(filepath, "markers")
    return df.to_json(orient="split")


# For information on the dash_uploader component and callbacks...
# See https://github.com/np-8/dash-uploader#example-with-callback-and-other-options
@app.callback(
    Output("metagenome-upload-store", "data"),
    [Input("upload-metagenome-data", "isCompleted")],
    [
        State("upload-metagenome-data", "fileNames"),
        State("upload-metagenome-data", "upload_id"),
    ],
)
def on_metagenome_upload(iscompleted, filenames, upload_id):
    try:
        filepath = validate_uploader(iscompleted, filenames, upload_id)
    except ValueError as err:
        logger.warn(err)
        raise PreventUpdate
    if not filepath:
        raise PreventUpdate
    df = file_to_db(filepath, "metagenome")
    return df.to_json(orient="split")


@app.callback(
    Output("modal-dismiss", "is_open"),
    [Input("open-dismiss", "n_clicks"), Input("close-dismiss", "n_clicks")],
    [State("modal-dismiss", "is_open")],
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


@app.callback(
    Output("refine-mags-button", "disabled"),
    [
        Input("binning-select", "value"),
        Input("markers-select", "value"),
        Input("metagenome-select", "value"),
    ],
)
def refine_mags_button_active_callback(binning_value, markers_value, metagenome_value):
    if binning_value is None or markers_value is None or metagenome_value is None:
        return True
    else:
        return False


@app.callback(
    Output("selected-tables-store", "data"),
    [
        Input("refine-mags-button", "n_clicks"),
        Input("binning-select", "value"),
        Input("markers-select", "value"),
        Input("metagenome-select", "value"),
    ],
)
def on_refine_mags_button_click(
    n, binning_select_value, markers_select_value, metagenome_select_value
):
    if n is None:
        raise PreventUpdate
    tables_dict = {}
    if binning_select_value is not None and markers_select_value is not None:
        marker_symbols_task = preprocess_marker_symbols.delay(
            binning_select_value, markers_select_value
        )
        # logger.debug(f"{type(marker_symbols_task)} {marker_symbols_task}")
        # tables_dict["marker_symbols"] = markers_select_value.replace("-markers","-marker-symbols")
    if metagenome_select_value is not None:
        tables_dict["metagenome"] = {"id": metagenome_select_value}
        embeddings_task = preprocess_embeddings(
            metagenome_table=metagenome_select_value,
            norm_method="am_clr",
            embed_methods=["densmap", "umap", "bhsne"],
        )
        # logger.debug(f"{type(embeddings_task)} {embeddings_task}")
        # tables_dict["embeddings"] = metagenome_select_value.replace("-metagenome","-embeddings")
    if binning_select_value is not None:
        tables_dict.update(
            {
                "binning": {"id": binning_select_value},
                "refinements": {
                    "id": binning_select_value.replace("-binning", "-refinement")
                },
            }
        )
        cluster_col = "cluster"
        clusters_geom_medians_task = preprocess_clusters_geom_medians.delay(
            binning_select_value, cluster_col
        )
        # logger.debug(f"{type(clusters_geom_medians_task)} {clusters_geom_medians_task}")
        # tables_dict["geom_medians"] = binning_select_value.replace("-binning",f"{cluster_col}-gmedians")
    if markers_select_value is not None:
        tables_dict["markers"] = {"id": markers_select_value}
    logger.debug(tables_dict)
    return SampleTables(**tables_dict).json()


@app.callback(
    Output("selected-tables-datatable", "children"),
    [
        Input("selected-tables-store", "data"),
        Input("tabs", "active_tab"),
    ],
    State("selected-tables-store", "data"),
)
def selected_tables_datatable_children(
    selected_tables_store_data: SampleTables,
    active_tab: str,
    new_selected_tables_store_data: SampleTables,
):
    # Why Input("tabs", "active_tab"): Navigating back to home tab triggers rendering of table from store
    if selected_tables_store_data is None:
        raise PreventUpdate
    samples = SampleTables.parse_raw(selected_tables_store_data)
    if new_selected_tables_store_data is not None:
        new_tables = SampleTables.parse_raw(new_selected_tables_store_data)
        if new_tables != samples:
            tables_dict = samples.dict()
            tables_dict.update(new_tables.dict())
            samples = SampleTables.parse_obj(tables_dict)

    has_table = False
    for __, table_id in samples:
        if table_id:
            has_table = True
            break

    if not has_table:
        raise PreventUpdate

    return DataTable(
        data=[
            {"filetype": sample, "table_id": table.id}
            for sample, table in samples
            if sample not in {"kmers"}
        ],
        columns=[
            {"id": "filetype", "name": "filetype", "editable": False},
            {"id": "table_id", "name": "table_id", "editable": False},
        ],
    )


@app.callback(
    Output("kmer-embed-tasks-button", "disabled"),
    Input("metagenome-select", "value"),
)
def refine_mags_button_active_callback(metagenome_value):
    if metagenome_value is None:
        return True
    else:
        return False


# TODO: Store final embeddings-table and retrieve for 2d scatterplot axes dropdowns/views
# from automappa.utils.serializers import get_table
# embed_df = get_table(embed_table_name, index_col='contig')


@app.callback(
    Output("embedding-tasks", "children"),
    Input("kmer-embed-tasks-button", "n_clicks"),
    Input("metagenome-select", "value"),
)
def on_compute_metagenome_kmer_embedding(btn_clicks: int, metagenome_select_value: str):
    if btn_clicks is None or metagenome_select_value is None:
        raise PreventUpdate
    embed_methods = ["densmap", "umap", "bhsne"]
    norm_method = "am_clr"
    task = preprocess_embeddings(
        metagenome_table=metagenome_select_value,
        norm_method=norm_method,
        embed_methods=embed_methods,
    )
    embed_table_name = metagenome_select_value.replace("-metagenome", "-embeddings")
    # TODO: Should create a polling or dcc.Interval(...) to construct this table for monitoring tasks status
    df = pd.DataFrame(
        [
            {
                "task_name": task.name,
                # "started": task.track_started,
                "state": task.state,
                "task_id": task.id,
                "norm_method": norm_method,
                "embed_methods": ",".join(embed_methods),
                "embed-table-name": embed_table_name,
            }
        ]
    )
    # logger.debug(df)
    return DataTable(
        data=df.to_dict("records"),
        columns=[{"id": col, "name": col, "editable": False} for col in df.columns],
        persistence=True,
        persistence_type="session",
    )
