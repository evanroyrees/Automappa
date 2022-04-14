# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path
from dash import html
from dash import dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.io as pio

import dash_uploader as du

from automappa.app import app
from automappa.utils.serializers import (
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
                        html.Div(id="output-binning-main-data-upload"),
                        html.Div(id="output-markers-data-upload"),
                        html.Div(id="output-metagenome-data-upload"),
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

binning_main_upload_store = dcc.Store(
    id="binning-main-upload-store", storage_type="local"
)

layout = dbc.Container(
    children=[
        binning_main_upload_store,
        dbc.Row(upload_modal),
        html.Br(),
        row_example_cards,
    ],
    fluid=True,
)


@app.callback(
    Output("binning-main-samples-cardheader", "children"),
    [Input("binning-main-upload-store", "modified_timestamp")],
    [State("binning-main-upload-store", "data")],
)
def on_binning_main_upload_store_data(timestamp, data):
    if timestamp is None:
        raise PreventUpdate
    if data is None:
        return "No samples uploaded"
    print(data)
    samples_count = len(data)
    if samples_count and samples_count == 1:
        return f"{samples_count} sample uploaded"
    return f"{samples_count} samples uploaded"


# TODO: Add Output('store-id', 'data') s.t. upload-id respective to files are available
# for later retrieval
# Chain callback... 
# Output("binning-main-upload-store", "data")
# Input('output-binning-main-data-upload', 'children'),
@app.callback(
    Output('output-binning-main-data-upload', 'children'),
    # Output("binning-main-upload-store", "data"),
    [Input('upload-binning-main-data', 'isCompleted')],
    [State('upload-binning-main-data', 'fileNames'),
     State('upload-binning-main-data', 'upload_id')],
)
def on_binning_main_upload(iscompleted, filenames, upload_id):
    if not iscompleted:
        return

    out = []
    if filenames is not None:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
            out.append(file)
        if len(out) > 1:
            return html.Div(f"You must only upload one file at a time! {len(out)} uploaded...")
        binning_main = out[0]
        session_uid = os.path.basename(os.path.dirname(binning_main))
        info = store_binning_main(binning_main, session_uid)
        return info
        # # return info, {upload_id: binning_main}
        # binning_main_filepath = str(binning_main.resolve())
        # if uploaded_data is None or upload_id not in uploaded_data:
        #     uploaded_data = {upload_id: [binning_main_filepath]}
        # elif upload_id in uploaded_data:
        #     uploaded_data[upload_id].append(binning_main_filepath)
        # return uploaded_data

    return html.Div("No Files Uploaded Yet!")

@app.callback(
    Output('output-markers-data-upload', 'children'),
    [Input('upload-markers-data', 'isCompleted')],
    [State('upload-markers-data', 'fileNames'),
     State('upload-markers-data', 'upload_id')],
)
def on_markers_upload(iscompleted, filenames, upload_id):
    if not iscompleted:
        return

    out = []
    if filenames is not None:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
            out.append(file)
        if len(out) > 1:
            return html.Div(f"You must only upload one file at a time! {len(out)} uploaded...")
        markers_fpath = out[0]
        session_uid = os.path.basename(os.path.dirname(markers_fpath))
        info = store_markers(markers_fpath, session_uid=session_uid)
        return info

    return html.Div("No Files Uploaded Yet!")

# For information on the dash_uploader component and callbacks...
# See https://github.com/np-8/dash-uploader#example-with-callback-and-other-options
@app.callback(
    Output('output-metagenome-data-upload', 'children'),
    [Input('upload-metagenome-data', 'isCompleted')],
    [State('upload-metagenome-data', 'fileNames'),
     State('upload-metagenome-data', 'upload_id')],
)
def on_metagenome_upload(iscompleted, filenames, upload_id):
    if not iscompleted:
        return

    out = []
    if filenames is not None:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
            out.append(file)
        if len(out) > 1:
            return html.Div(f"You must only upload one file at a time! {len(out)} uploaded...")
        filepath = out[0]
        session_uid = os.path.basename(os.path.dirname(filepath))
        info = store_metagenome(filepath, session_uid=session_uid)
        return info

    return html.Div("No Files Uploaded Yet!")


@app.callback(
    Output("modal-dismiss", "is_open"),
    [Input("open-dismiss", "n_clicks"), Input("close-dismiss", "n_clicks")],
    [State("modal-dismiss", "is_open")],
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open
