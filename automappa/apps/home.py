# -*- coding: utf-8 -*-

from datetime import datetime
import os
import logging
from pathlib import Path
from dash import html, dcc
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.io as pio

import dash_uploader as du

from automappa.app import app
from automappa.utils.serializers import (
    convert_bytes,
    store_binning_main,
    store_markers,
    store_metagenome,
)

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)

pio.templates.default = "plotly_white"

UPLOAD_FOLDER_ROOT = os.environ.get("UPLOAD_FOLDER_ROOT")

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

# html.Div(id="output-binning-main-data-upload"),
html.Div(id="output-markers-data-upload"),
html.Div(id="output-metagenome-data-upload"),

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

binning_main_upload_store = dcc.Store(
    id="binning-main-upload-store", storage_type="local"
)
markers_upload_store = dcc.Store(id="markers-upload-store", storage_type="local")
metagenome_upload_store = dcc.Store(id="metagenome-upload-store", storage_type="local")
samples_store = dcc.Store(id="samples-store", storage_type="local")

# samples_datatable = html.Div(id="samples-datatable")
samples_datatable = dcc.Loading(
        id="loading-samples-datatable",
        children=[html.Div(id="samples-datatable")],
        type="dot",
        color="#646569",
    ),

layout = dbc.Container(
    children=[
        binning_main_upload_store,
        markers_upload_store,
        metagenome_upload_store,
        samples_store,
        dbc.Row(upload_modal),
        html.Br(),
        # row_example_cards,
        dbc.Row(samples_datatable),
    ],
    fluid=True,
)


@app.callback(
    Output('samples-store', 'data'),
    [
        Input("binning-main-upload-store", "modified_timestamp"),
        Input("markers-upload-store", "modified_timestamp"),
        Input("metagenome-upload-store", "modified_timestamp"),
    ],
    [
    State("binning-main-upload-store", "data"),
    State("markers-upload-store", "data"),
    State("metagenome-upload-store", "data"),
    State('samples-store', 'data'),
    ],
)
def on_binning_main_upload_store_data(
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
    ):
        raise PreventUpdate
    if (
        binning_uploads_timestamp is None
        and markers_uploads_timestamp is None
        and metagenome_uploads_timestamp is None
    ):
        raise PreventUpdate
    # We need to ensure we prevent an update if there has not been one, otherwise all of our datastore
    # gets removed...
    binning_samples_df = pd.read_json(binning_uploads, orient="split") if binning_uploads else pd.DataFrame()
    marker_samples_df = pd.read_json(markers_uploads, orient="split") if markers_uploads else pd.DataFrame()
    metagenome_samples_df = pd.read_json(metagenome_uploads, orient="split") if metagenome_uploads else pd.DataFrame()
    samples_store_df = pd.read_json(samples_store_data, orient='split') if samples_store_data else pd.DataFrame()
    samples_df = pd.concat(
        [
            samples_store_df,
            binning_samples_df,
            marker_samples_df, 
            metagenome_samples_df,
        ]
    ).drop_duplicates(subset=["table_id"])

    logger.debug(f"{samples_df.shape[0]:,} samples retrieved from data upload stores")

    return samples_df.to_json(orient='split')

@app.callback(
    Output("samples-datatable", "children"),
    [Input('samples-store', 'data')],
    State('samples-store', 'data'),
)
def on_samples_store_data(samples_store_data, new_samples_store_data):
    # if samples_store_data is None:
    #     # Show upload button...?
    #     raise PreventUpdate

    # import pdb;pdb.set_trace()

    samples_df = pd.read_json(samples_store_data, orient='split')
    if new_samples_store_data is not None:
        new_samples_df = pd.read_json(new_samples_store_data, orient='split')
        samples_df = pd.concat([samples_df, new_samples_df]).drop_duplicates(subset=['table_id'])

    logger.debug(f"retrieved {samples_df.shape[0]:,} samples from samples store")

    if samples_df.empty:
        raise PreventUpdate

    return DataTable(
        data=samples_df.to_dict("records"),
        columns=[{"id": col, "name": col, "editable": False} for col in samples_df.columns],
        
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
    if not iscompleted:
        return
    if filenames is None:
        return
    if upload_id:
        root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
    else:
        root_folder = Path(UPLOAD_FOLDER_ROOT)

    uploaded_files = []
    for filename in filenames:
        file = root_folder / filename
        uploaded_files.append(file)

    if len(uploaded_files) > 1:
        logger.error("You may only upload one file at a time!")
        raise PreventUpdate

    filepath = uploaded_files[0]
    filename = os.path.basename(filepath)
    unit = "MB"
    filesize = convert_bytes(os.path.getsize(filepath), unit)
    timestamp = os.path.getmtime(filepath)
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    table_id = store_binning_main(filepath)

    return pd.DataFrame(
        [
            {
                "filetype": "binning_main",
                "filename": filename,
                f"filesize ({unit})": filesize,
                "table_id": table_id,
                "uploaded": last_modified,
                "timestamp": timestamp,
            }
        ]
    ).to_json(orient="split")


@app.callback(
    Output("markers-upload-store", "data"),
    [Input("upload-markers-data", "isCompleted")],
    [
        State("upload-markers-data", "fileNames"),
        State("upload-markers-data", "upload_id"),
    ],
)
def on_markers_upload(iscompleted, filenames, upload_id):
    if not iscompleted:
        return
    if filenames is None:
        return
    if upload_id:
        root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
    else:
        root_folder = Path(UPLOAD_FOLDER_ROOT)

    uploaded_files = []
    for filename in filenames:
        file = root_folder / filename
        uploaded_files.append(file)
    if len(uploaded_files) > 1:
        logger.error("You may only upload one file at a time!")
        raise PreventUpdate

    filepath = uploaded_files[0]
    filename = os.path.basename(filepath)
    unit = "MB"
    filesize = convert_bytes(os.path.getsize(filepath), unit)
    timestamp = os.path.getmtime(filepath)
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    table_id = store_markers(filepath)

    return pd.DataFrame(
        [
            {
                "filetype": "markers",
                "filename": filename,
                f"filesize ({unit})": filesize,
                "timestamp": timestamp,
                "uploaded": last_modified,
                "table_id": table_id,
            }
        ]
    ).to_json(orient="split")


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
    if not iscompleted:
        return
    if filenames is None:
        return
    if upload_id:
        root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
    else:
        root_folder = Path(UPLOAD_FOLDER_ROOT)

    uploaded_files = []
    for filename in filenames:
        file = root_folder / filename
        uploaded_files.append(file)
    if len(uploaded_files) > 1:
        logger.error("You may only upload one file at a time!")
        raise PreventUpdate

    filepath = uploaded_files[0]
    filename = os.path.basename(filepath)
    unit = "MB"
    filesize = convert_bytes(os.path.getsize(filepath), unit)
    timestamp = os.path.getmtime(filepath)
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    table_id = store_metagenome(filepath)

    return pd.DataFrame(
        [
            {
                "filetype": "metagenome",
                "filename": filename,
                f"filesize ({unit})": filesize,
                "timestamp": timestamp,
                "uploaded": last_modified,
                "table_id": table_id,
            }
        ]
    ).to_json(orient="split")


@app.callback(
    Output("modal-dismiss", "is_open"),
    [Input("open-dismiss", "n_clicks"), Input("close-dismiss", "n_clicks")],
    [State("modal-dismiss", "is_open")],
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open
