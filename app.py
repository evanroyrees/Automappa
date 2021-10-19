import os
import flask
import dash
from io import TextIOWrapper

import pandas as pd

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
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


def GC(seq):
    """Calculate G+C content, return percentage (as float between 0 and 100).
    Copes with mixed case sequences, and with the ambiguous nucleotide S (G or C)
    when counting the G and C content.

    Note
    ----
    Adopted from Biopython.SeqUtils, but not installing biopython to reduce overhead.
    (Biopython package is a heavy dependency. We are trying to keep things lite...)

    The percentage is calculated against the full length, e.g.:
    >>> from Bio.SeqUtils import GC
    >>> GC("ACTGN")
    40.0
    Note that this will return zero for an empty sequence.
    """
    gc = sum(seq.count(x) for x in ["G", "C", "g", "c", "S", "s"])
    try:
        return gc * 100.0 / len(seq)
    except ZeroDivisionError:
        return 0.0


def fasta_parser(handle: TextIOWrapper):
    for line in handle:
        if line[0] == ">":
            title = line[1:].rstrip()
            contig_id = title.split(None, 1)[0]
            break
    else:
        # no break encountered - probably an empty file
        return
    seq_lines = ""
    for line in handle:
        if line[0] == ">":
            yield title, seq_lines
            seq_lines = ""
            title = line[1:].rstrip()
            contig_id = title.split(None, 1)[0]
            continue
        else:
            seq_lines += line.strip().replace(" ", "").replace("\r", "")
    yield contig_id, seq_lines
