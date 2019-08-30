# -*- coding: utf-8 -*-
import math
import json
from datetime import date
import dateutil.parser

import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go


from app import app, indicator, millify, df_to_table, parse_contents #am_manager

def modal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # modal header
                        html.Div(
                            [
                                html.Span(
                                    "Upload Autometa Results Table",
                                    style={
                                        "color": "#c5040d",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="analysis_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="row",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),
                        # modal form
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Length Cutoff",
                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="length_cutoff",
                                    placeholder="Length Cutoff (default 3000bp)",
                                    type="text",
                                    value="3000",
                                    style={"width": "100%"},
                                ),
                                html.P(
                                    style={
                                        "textAlign": "left",
                                        "marginBottom": "2",
                                        "marginTop": "4",
                                    },
                                    id="completeness_display"
                                ),
                                dcc.Slider(
                                    id="completeness_cutoff",
                                    min=5.0,
                                    max=100.0,
                                    value=20.0,
                                    updatemode="drag",
                                ),
                                html.P(
                                    "Select Metagenome Assembly",
                                    style={
                                        "textAlign": "left",
                                        "marginBottom": "2",
                                        "marginTop": "4",
                                    },
                                ),
                                dcc.Upload(
                                    id='upload-data',
                                    children=['Drag and Drop or ', html.A('Select a File')],
                                    style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight':' 60px',
                                        'borderWidth': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                    },

                                )
                            ],
                            className="row",
                            style={"padding": "2% 8%"},
                        ),
                        # submit button
                        html.Span(
                            "Submit",
                            id="submit_new_analysis",
                            n_clicks=0,
                            className="button button--primary add"
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="analysis_modal",
        style={"display": "none"},
    )

layout = [

    # top controls
    html.Div(
        [
            #add button
            html.Div(
                html.Span(
                    "New Analysis",
                    id="new_project",
                    n_clicks=0,
                    className="button button--primary add",
                ),
                className="two columns",
                style={"float": "right"},
            ),

            # Add html.Form()
            # https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#uploading-files
            # https://github.com/plotly/dash-html-components/blob/master/dash_html_components/Form.py
        ],
        className="row",
        style={"marginBottom": "10"},
    ),
    modal(),
]

@app.callback(
    Output('user_projects', 'children'),
    [Input("binning_df", "children")]
)
def get_projects(df):
    df = pd.read_json(df, orient="split")

# hide/show modal
@app.callback(Output("analysis_modal", "style"), [Input("new_project", "n_clicks")])
def display_analysis_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}

# reset to 0 add button n_clicks property
@app.callback(
    Output("new_project", "n_clicks"),
    [Input("analysis_modal_close", "n_clicks"), Input("submit_new_analysis", "n_clicks")],
)
def close_modal_callback(n, n2):
    return 0

@app.callback(
    Output("completeness_display", "children"),
    [Input("completeness_cutoff", "value")]
)
def display_modal_completeness_cutoff(completeness):
    return 'Completeness Cutoff:\t{}%'.format(completeness)


# Start new analysis given autometa parameters and new metagenome dataset
@app.callback(
    Output("uploaded-data", "children"),
    [
        Input("submit_new_analysis", "n_clicks"),
    ],
    [
        State("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
        State("completeness_cutoff", "value"),
        State("length_cutoff", "value"),
    ],
)
def results_upload(n_clicks, contents, fname, last_modified, completeness, length):
    if n_clicks > 0:
        query = {
            "length": length,
            "completeness": completeness,
            "filename": fname,
            "last_modified": last_modified,
            "contents": contents,
        }
        # am_manager.add_project(query)
        # df = am_manager.get_project(fname)
        # return df.to_json(orient="split")

        return parse_df_upload(contents,fname,last_modified)
    return
