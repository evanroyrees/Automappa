import os
import flask
import dash
from io import TextIOWrapper
import dash_bootstrap_components.themes as dbct

import pandas as pd

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbct.SANDSTONE])
app.config.suppress_callback_exceptions = True


def load_markers(markers: str) -> pd.DataFrame:
    """Read markers table into specified `format`.

    Parameters
    ----------

    markers : str
        </path/to/`kingdom`.markers.tsv>

    Returns
    -------
    pd.DataFrame or dict
        index=range(0, num_marker_contigs), cols=[contig, domain sacc,..]

    Raises
    -------
    FileNotFoundError
        Provided `markers` does not exist

    """
    if not os.path.exists(markers) or not os.path.getsize(markers):
        raise FileNotFoundError(markers)
    df = pd.read_csv(markers, sep="\t", index_col="contig")
    markers_grouped_by_contigs = df.groupby("contig")["sacc"]
    return markers_grouped_by_contigs.value_counts().unstack().reset_index()
    