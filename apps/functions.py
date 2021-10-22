# functions that don't return HTML
import pandas as pd
from pandas import DataFrame
import numpy as np
import os
import math

def load_markers(markers: str) -> DataFrame:
    """Read markers table into specified `format`.

    Parameters
    ----------

    markers : str
        </path/to/`kingdom`.markers.tsv>

    Returns
    -------
    DataFrame or dict
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


def get_assembly_stats(df: DataFrame, column):
    metrics = {"n50": {}, "clusters": {}}
    bins = dict(list(df.groupby(column)))
    for cluster, dff in bins.items():
        # 1. Determine cluster n50
        lengths = sorted(dff.length.tolist(), reverse=True)
        half_size = dff.length.sum() / 2
        total, n50 = 0, None
        for l in lengths:
            total += l
            if total >= half_size:
                n50 = l
                break
        metrics["n50"].update({cluster: n50})
        metrics["clusters"].update({cluster: cluster})
    ftuples = [("n_ctgs", "count"), ("size", "sum"), ("max_len", "max")]
    clusters = df.groupby(column)
    agg_stats = clusters["length"].agg(ftuples)
    metrics.update(agg_stats.to_dict())
    # Get weighted averages of GC percentages
    get_gc_wtdavg = lambda g: round(
        np.average(g["gc"], weights=(g.length / g.length.sum())), 2
    )
    wtd_gcs = clusters.apply(get_gc_wtdavg)
    # Get weighted standard deviation
    get_wtd_gcs_sdpc = lambda g: round(
        (
            math.sqrt(
                np.average(
                    (g["gc"] - np.average(g["gc"], weights=(g.length / g.length.sum())))
                    ** 2,
                    weights=(g.length / g.length.sum()),
                )
            )
            / np.average(g["gc"], weights=(g.length / g.length.sum()))
        )
        * 100,
        2,
    )
    wtd_gcs_sdpc = clusters.apply(get_wtd_gcs_sdpc)
    # weighted_gc_sdpc = (weighted_gc_stdev / weighted_gc_av)*100
    metrics.update(
        {"wtd_gcs": wtd_gcs.to_dict(), "wtd_gc_sdpc": wtd_gcs_sdpc.to_dict()}
    )

    # Get weighted average of Coverages
    get_cov_wtdavg = lambda g: round(
        np.average(g["cov"], weights=(g.length / g.length.sum())), 2
    )
    wtd_covs = clusters.apply(get_cov_wtdavg)
    # Get weighted standard deviation and calculate z-score...
    get_wtd_covs_sdpc = lambda g: round(
        (
            math.sqrt(
                np.average(
                    (
                        g["cov"]
                        - np.average(g["cov"], weights=(g.length / g.length.sum()))
                    )
                    ** 2,
                    weights=(g.length / g.length.sum()),
                )
            )
            / np.average(g["cov"], weights=(g.length / g.length.sum()))
        )
        * 100,
        2,
    )
    wtd_covs_sdpc = clusters.apply(get_wtd_covs_sdpc)
    metrics.update(
        {"wtd_covs": wtd_covs.to_dict(), "wtd_cov_sdpc": wtd_covs_sdpc.to_dict()}
    )
    return DataFrame(
        {
            "cluster": metrics["clusters"],
            "size": metrics["size"],
            "longest_contig": metrics["max_len"],
            "n50": metrics["n50"],
            "number_contigs": metrics["n_ctgs"],
            "wtd_cov": metrics["wtd_covs"],
            "wtd_cov_sdpc": metrics["wtd_cov_sdpc"],
            "wtd_gc": metrics["wtd_gcs"],
            "wtd_gc_sdpc": metrics["wtd_gc_sdpc"],
        }
    )

if __name__ == "__main__":
    pass