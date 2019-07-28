
import math
import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dateutil.parser
import base64
import io
import datetime

    # from sfManager import sf_Manager

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
app.config.suppress_callback_exceptions = True

# sf_manager = sf_Manager()

# return html Table with dataframe values
def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [
            html.Tr(
                [
                    html.Td(df.iloc[i][col])
                    for col in df.columns
                ]
            )
            for i in range(len(df))
        ]
    )


#returns most significant part of a number
def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


#returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [

            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id = id_value,
                className="indicator_value"
            ),
        ],
        className="four columns indicator",

    )

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    errorMsg = html.Div([
        'Error processing {}. Please upload an Autometa output table'.format(filename)
    ])
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'tab' in filename or 'tsv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return errorMsg
    except Exception as e:
        print(e)
        return errorMsg
    return html.Div(df.to_json(orient='split'), id="binning_df", style={"display": "none"})

def parse_df_upload(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    errorMsg = html.Div([
        'Error processing {}. Please upload an Autometa output table'.format(filename)
    ])
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'tab' in filename or 'tsv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return errorMsg
    except Exception as e:
        print(e)
        return errorMsg
    return html.Div(df.to_json(orient='split'), id="binning_df", style={"display": "none"})
