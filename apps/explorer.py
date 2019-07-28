# -*- coding: utf-8 -*-


import os
import sys
import json
import math
import base64
import datetime
import io

import pandas as pd
import numpy as np
import flask

import dash
# import dash_cytoscape as cyto
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import plotly.plotly as py

from app import app, indicator, millify, df_to_table, parse_df_upload, parse_contents

# returns choropleth map figure based on status filter
# def choropleth_map(status, df):
#     if status == "open":
#         df = df[
#             (df["Status"] == "Open - Not Contacted")
#             | (df["Status"] == "Working - Contacted")
#         ]
#
#     elif status == "converted":
#         df = df[df["Status"] == "Closed - Converted"]
#
#     elif status == "lost":
#         df = df[df["Status"] == "Closed - Not Converted"]
#
#     df = df.groupby("State").count()
#
#     scl = [[0.0, "rgb(38, 78, 134)"], [1.0, "#0091D5"]] # colors scale
#
#     data = [
#         dict(
#             type="choropleth",
#             colorscale=scl,
#             locations=df.index,
#             z=df["Id"],
#             locationmode="USA-states",
#             marker=dict(line=dict(color="rgb(255,255,255)", width=2)),
#         )
#     ]
#
#     layout = dict(
#         geo=dict(
#             scope="usa",
#             projection=dict(type="albers usa"),
#             lakecolor="rgb(255, 255, 255)",
#         ),
#         margin=dict(l=10, r=10, t=0, b=0),
#     )
#     return dict(data=data, layout=layout)


# returns pie chart that shows lead source repartition
# def lead_source(status, df):
#     if status == "open":
#         df = df[
#             (df["Status"] == "Open - Not Contacted")
#             | (df["Status"] == "Working - Contacted")
#         ]
#
#     elif status == "converted":
#         df = df[df["Status"] == "Closed - Converted"]
#
#     elif status == "lost":
#         df = df[df["Status"] == "Closed - Not Converted"]
#
#     nb_leads = len(df.index)
#     types = df["LeadSource"].unique().tolist()
#     values = []
#
#     # compute % for each leadsource type
#     for case_type in types:
#         nb_type = df[df["LeadSource"] == case_type].shape[0]
#         values.append(nb_type / nb_leads * 100)
#
#     trace = go.Pie(
#         labels=types,
#         values=values,
#         marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
#     )
#
#     layout = dict(margin=dict(l=15, r=10, t=0, b=65), legend=dict(orientation="h"))
#     return dict(data=[trace], layout=layout)



# def converted_leads_count(period, df):
#     df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")
#     df = df[df["Status"] == "Closed - Converted"]
#
#     df = (
#         df.groupby([pd.Grouper(key="CreatedDate", freq=period)])
#         .count()
#         .reset_index()
#         .sort_values("CreatedDate")
#     )
#
#     trace = go.Scatter(
#         x=df["CreatedDate"],
#         y=df["Id"],
#         name="converted leads",
#         fill="tozeroy",
#         fillcolor="#e6f2ff",
#     )
#
#     data = [trace]
#
#     layout = go.Layout(
#         xaxis=dict(showgrid=False),
#         margin=dict(l=33, r=25, b=37, t=5, pad=4),
#         paper_bgcolor="white",
#         plot_bgcolor="white",
#     )
#
#     return {"data": data, "layout": layout}


normalizeLen = lambda x: np.ceil(((x.length-x.length.min())/(x.length.max()-x.length.min()))*11+4)


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
                            id="submit_new_lead",
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
            html.Div(
                dcc.Dropdown(
                    id="zaxis_column",
                    options=[
                        {"label": "Coverage", "value": "cov"},
                        {"label": "GC%", "value": "gc"},
                        {"label": "Length", "value": "length"},
                    ],
                    value="cov",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(
                dcc.Dropdown(
                    id="cluster_col",
                    options=[
                        {"label": "Cluster", "value": "cluster"},
                        {"label": "Decision Tree Classifier", "value": "ML_expanded_clustering"},
                        {"label": "Paired-end Refinement", "value": "paired_end_refined_bin"},
                        # {"label": "Grid Search", "value": "lost"},
                    ],
                    value="cluster",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(
                dcc.Dropdown(
                    id="2d_xaxis",
                    options=[
                        {'label':'bh-tsne-x','value':'bh_tsne_x'},
                        {'label':'Coverage','value':'cov'},
                        {'label':'GC%','value':'gc'},
                        {'label':'Length','value':'length'},
                    ],
                    value="bh_tsne_x",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(
                dcc.Dropdown(
                    id="2d_yaxis",
                    options=[
                        {'label':'bh-tsne-y','value':'bh_tsne_y'},
                        {'label':'Coverage','value':'cov'},
                        {'label':'GC%','value':'gc'},
                        {'label':'Length','value':'length'},
                    ],
                    value="bh_tsne_y",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(
                dcc.Dropdown(
                    id="rank_dropdown",
                    options=[
                        {'label':'Kingdom','value':'kingdom'},
                        {'label':'Phylum','value':'phylum'},
                        {'label':'Class','value':'class'},
                        {'label':'Order','value':'order'},
                        {'label':'Family','value':'family'},
                        {'label':'Genus','value':'genus'},
                        {'label':'Species','value':'species'},
                    ],
                    value="phylum",
                    clearable=False,
                ),
                className="two columns",
            ),
            # add button
            html.Div(
                html.Span(
                    "Upload Results",
                    id="new_analysis",
                    n_clicks=0,
                    className="button button--primary",
                    style={
                        "height": "34",
                        "background": "#c5040d",
                        "border": "1px solid #c5040d",
                        "color": "white",
                    },
                ),
                className="two columns",
                style={"float": "right"},
            ),
        ],
        className="row",
        style={"marginBottom": "10"},
    ),

    # indicators row div
    html.Div(
        [
            indicator(
                "#00cc96", "Marker Sets", "marker_sets"
            ),
            indicator(
                "#119DFF", "Completeness", "selected_completeness"
            ),
            indicator(
                "#EF553B",
                "Purity",
                "selected_purity",
            ),
        ],
        className="row",
    ),

    # charts row div
    html.Div(
        [
            html.Div(
                [
                    html.P("3D Binning Overview"),
                    dcc.Graph(
                        id='scatter3d_graphic',
                        clear_on_unhover=True,
                        style={"height": "90%", "width": "98%"},
                        config={
                            'toImageButtonOptions':dict(
                                format='svg',
                                filename='scatter3dPlot.autometa.binning',
                            ),
                            # 'displayModeBar':False,
                        }
                    ),
                ],
                className="four columns chart_div"
            ),

            html.Div(
                [
                    html.P("2D Binning Overview"),
                    dcc.Graph(
                        id='scatter2d_graphic',
                        style={"height": "90%", "width": "98%"},
                        clear_on_unhover=True,
                    ),
                ],
                className="four columns chart_div"
            ),

            html.Div(
                [
                    html.P("Taxa Distribution"),
                    dcc.Graph(
                        id='taxa_piechart',
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),
        ],
        className="row",
        style={"marginTop": "5"},
    ),

    # table div
    html.Div(
        className="row",
        style={
            "maxHeight": "350px",
            "overflowY": "scroll",
            "padding": "8",
            "marginTop": "5",
            "backgroundColor":"white",
            "border": "1px solid #C8D4E3",
            "borderRadius": "3px"
        },
        id='binning_table'
    ),
    html.Div(id='uploaded-data'),

    modal(),
]


# updates left indicator based on df updates
@app.callback(
    Output("marker_sets", "children"),
    [Input("scatter2d_graphic", "selectedData"),
    Input("cluster_col", "value"),
    Input("binning_df", "children")]
)
def selected_marker_sets_callback(selectedData, clusterCol, df):
    if not selectedData:
        return '-'
    # Update to return total number of bins
    df = pd.read_json(df, orient='split')
    ctg_list = {point['text'] for point in selectedData['points']}
    pfams = df[df.contig.isin(ctg_list)].single_copy_PFAMs.dropna().tolist()
    all_pfams = [p for pfam in pfams for p in pfam.split(',')]
    total = len(all_pfams)
    n_marker_sets = round(float(total)/139, 2)
    marker_sets = '{} ({} markers)'.format(n_marker_sets, total)
    return marker_sets


# updates middle indicator based on selected contigs in 2d scatter plot
@app.callback(
    Output("selected_completeness", "children"),
    [Input("scatter2d_graphic", "selectedData"),
    Input("binning_df", "children")]
)
def selected_completeness_callback(selectedData, df):
    if not selectedData:
        return '-'
    df = pd.read_json(df, orient='split')
    ctg_list = {point['text'] for point in selectedData['points']}
    pfams = df[df.contig.isin(ctg_list)].single_copy_PFAMs.dropna().tolist()
    all_pfams = [p for pfam in pfams for p in pfam.split(',')]
    markers = 139
    nunique = len(set(all_pfams))
    completeness = round(float(nunique)/markers * 100, 2)
    return str(completeness)


# updates right indicator based on selected contigs in 2d scatter plot
@app.callback(
    Output("selected_purity", "children"),
    [Input("scatter2d_graphic", "selectedData"),
    Input("binning_df", "children")]
)
def selected_purity_callback(selectedData, df):
    if not selectedData:
        return '-'
    df = pd.read_json(df, orient='split')
    ctg_list = {point['text'] for point in selectedData['points']}
    pfams = df[df.contig.isin(ctg_list)].single_copy_PFAMs.dropna().tolist()
    all_pfams = [p for pfam in pfams for p in pfam.split(',')]
    total = len(all_pfams)
    nunique = len(set(all_pfams))
    purity = '-' if total == 0 else round(float(nunique)/total * 100, 2)
    return str(purity)


# update pie chart figure based on dropdown's value and df updates
# @app.callback(
#     Output("lead_source", "figure"),
#     [Input("lead_source_dropdown", "value"), Input("leads_df", "children")],
# )
# def lead_source_callback(status, df):
#     df = pd.read_json(df, orient="split")
#     return lead_source(status, df)


@app.callback(
    Output("binning_table", "children"),
    [Input("binning_df", "children")],
)
def bin_table_callback(df):
    df = pd.read_json(df, orient="split")
    child = dash_table.DataTable(
        id='datatable',
        data=df.to_dict('records'),
        columns=[{'name':col, 'id':col} for col in df.columns],
        # sorting=True,
        # filtering=True,
        virtualization=True,
        # pagination_mode=None,
    ),
    return child


@app.callback(
    Output("taxa_piechart", "figure"),
    [Input("scatter2d_graphic", "selectedData"),
    Input("rank_dropdown", "value"),
    Input("binning_df", "children")]
)
def taxa_piechart_callback(selectedData, selectedRank, df):
    df = pd.read_json(df, orient="split")
    layout = dict(margin=dict(l=15, r=10, t=35, b=45))
    if not selectedData:
        n_ctgs = len(df.index)
        labels = df[selectedRank].unique().tolist()
        values = [len(df[df[selectedRank] == label])/float(n_ctgs) for label in labels]
        trace = go.Pie(
            labels=labels,
            values=values,
            textinfo='label',
            hoverinfo='label+percent',
            showlegend=False,
        )
        return dict(data=[trace], layout=layout)

    ctg_list = {point['text'] for point in selectedData['points']}
    dff = df[df.contig.isin(ctg_list)]
    n_ctgs = len(dff.index)
    labels = dff[selectedRank].unique().tolist()
    values = [len(dff[dff[selectedRank] == label])/float(n_ctgs) for label in labels]
    trace = go.Pie(
        labels=labels,
        values=values,
        hoverinfo='label+percent',
        textinfo='label',
        showlegend=False,
    )
    return dict(data=[trace], layout=layout)


@app.callback(
    Output('scatter3d_graphic', 'figure'),
    [Input('zaxis_column', 'value'),
    Input("cluster_col", "value"),
    Input('scatter2d_graphic','selectedData'),
    Input("binning_df", "children")])
def update_zaxis(zaxis_column, cluster_col, selectedData, df):
    df = pd.read_json(df, orient="split")
    titles = {
        'cov':'Coverage',
        'gc':'GC%',
        'length':'Length',
    }
    zaxis_title = titles[zaxis_column]
    if selectedData is None:
        selected = df.contig.tolist()
    else:
        selected = {point['text'] for point in selectedData['points']}

    dff = df[df.contig.isin(selected)]


    return {
        'data': [
            go.Scatter3d(
                x=dff[dff[cluster_col] == i]['bh_tsne_x'],
                y=dff[dff[cluster_col] == i]['bh_tsne_y'],
                z=dff[dff[cluster_col] == i][zaxis_column],
                text=dff[dff[cluster_col] == i]['contig'],
                mode='markers',
                textposition='top center',
                opacity=0.45,
                hoverinfo='all',
                marker={
                    'size': dff.assign(normLen = normalizeLen)['normLen'],
                    'line': {'width': 0.1, 'color': 'black'},
                },
                name=i
            ) for i in dff[cluster_col].unique()
        ],
        'layout': go.Layout(
            scene = dict(
                xaxis=dict(title='bh-tsne-x'),
                yaxis=dict(title='bh-tsne-y'),
                zaxis=dict(title=zaxis_title),
            ),
            legend={'x': 0, 'y': 1},
            autosize=True,
            margin=dict(r=0, b=0, l=0, t=25),
            # title='3D Clustering Visualization',
            hovermode='closest',
        ),
    }


@app.callback(
    Output('scatter2d_graphic', 'figure'),
    [Input('2d_xaxis', 'value'),
    Input('2d_yaxis', 'value'),
    Input('cluster_col', 'value'),
    Input("binning_df", "children"),
    # Input('datatable', 'data')]
])
def update_axes(xaxis_column, yaxis_column, cluster_col, df):
    df = pd.read_json(df, orient="split")
    titles = {
        'bh_tsne_x':'bh-tsne-x',
        'bh_tsne_y':'bh-tsne-y',
        'cov':'Coverage',
        'gc':'GC%',
        'length':'Length',
    }
    xaxis_title = titles[xaxis_column]
    yaxis_title = titles[yaxis_column]
    # See: https://codeburst.io/notes-from-the-latest-plotly-js-release-b035a5b43e21
    # contigs = {point['contig'] for point in data}
    # dff = df[df.contig.isin(contigs)]
    # selected = dff.index.tolist()
    return {
        'data': [
            go.Scattergl(
                x=df[df[cluster_col] == i][xaxis_column],
                y=df[df[cluster_col] == i][yaxis_column],
                text=df[df[cluster_col] == i]['contig'],
                mode='markers',
                opacity=0.45,
                marker={
                    'size': df.assign(normLen = normalizeLen)['normLen'],
                    'line': {'width': 0.1, 'color': 'black'},
                },
                name=i
            ) for i in df[cluster_col].unique()
        ],
        'layout': go.Layout(
            scene = dict(
                xaxis=dict(title=xaxis_title),
                yaxis=dict(title=yaxis_title),
            ),
            legend={'x': 1, 'y': 1},
            autosize=True,
            margin=dict(r=0, b=0, l=0, t=25),
            # title='2D Clustering Visualization',
            hovermode='closest',
        ),
    }


@app.callback(
    Output('datatable', 'data'),
    [Input('scatter2d_graphic','selectedData'),
    Input("binning_df", "children")]
)
def update_table(selectedData, df):
    df = pd.read_json(df, orient="split")
    if selectedData is None:
        return df.to_dict('records')
    selected = {point['text'] for point in selectedData['points']}
    return df[df.contig.isin(selected)].to_dict('records')

# update table based on dropdown's value and df updates
# @app.callback(
#     Output("leads_table", "children"),
#     [Input("lead_source_dropdown", "value"), Input("leads_df", "children")],
# )
# def leads_table_callback(status, df):
#     df = pd.read_json(df, orient="split")
#     if status == "open":
#         df = df[
#             (df["Status"] == "Open - Not Contacted")
#             | (df["Status"] == "Working - Contacted")
#         ]
#     elif status == "converted":
#         df = df[df["Status"] == "Closed - Converted"]
#     elif status == "lost":
#         df = df[df["Status"] == "Closed - Not Converted"]
#     df = df[["CreatedDate", "Status", "Company", "State", "LeadSource"]]
#     return df_to_table(df)


# update pie chart figure based on dropdown's value and df updates
# @app.callback(
#     Output("converted_leads", "figure"),
#     [Input("converted_leads_dropdown", "value"), Input("leads_df", "children")],
# )
# def converted_leads_callback(period, df):
#     df = pd.read_json(df, orient="split")
#     return converted_leads_count(period, df)


# hide/show modal
@app.callback(Output("analysis_modal", "style"), [Input("new_analysis", "n_clicks")])
def display_analysis_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


# reset to 0 add button n_clicks property
@app.callback(
    Output("new_analysis", "n_clicks"),
    [Input("analysis_modal_close", "n_clicks"), Input("submit_new_lead", "n_clicks")],
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
        Input("submit_new_lead", "n_clicks"),
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
