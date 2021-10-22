# functions that don't return HTML
import pandas as pd
import numpy as np
import os


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

if __name__ == "__main__":
    pass