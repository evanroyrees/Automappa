# -*- coding: utf-8 -*-

from dash import html
import dash_bootstrap_components as dbc
import plotly.io as pio


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


example_card = dbc.Card(
    [
        dbc.CardHeader("{Sample Name}"),
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
        dbc.Col(example_card, width=card_widths),
        dbc.Col(example_card, width=card_widths),
        dbc.Col(example_card, width=card_widths),
    ]
)

layout = dbc.Container(
    children=[
        html.Br(),
        row_example_cards,
        html.Br(),
        row_example_cards,
        html.Br(),
        row_example_cards,
        html.Br(),
    ],
    fluid=True,
)
