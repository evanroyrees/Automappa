#!/usr/bin/env python



import os
import glob
import pandas as pd

from geom_median.numpy import compute_geometric_median
from celery import Celery, chain
from dotenv import load_dotenv
from autometa.common.external import hmmscan

load_dotenv()

REDIS_URL = os.environ.get('REDIS_URL')
BROKER_URL = os.environ.get('BROKER_URL')

CELERY = Celery('tasks', backend=REDIS_URL, broker=BROKER_URL)


# TODO: Data loader
# TODO: Create 2d-scatterplot figure
# TODO: Marker symbols
# TODO: CheckM annotation
# TODO: kmer freq. analysis pipeline
# TODO: scatterplot 2-d embedding views

@CELERY.task
def hmmdb_formatter(hmmdb) -> None:
    hmmscan.hmmpress(hmmdb)


@CELERY.task
def scanner(seqfile, hmmdb, out) -> str:
    # NOTE: returns outfpath
    # cmd = [
    #     "hmmscan",
    #     "--cpu",
    #     "1",
    #     "--seed",
    #     "42",
    #     "--tblout",
    #     out,
    #     hmmdb,
    #     seqfile
    # ]
    # run_cmd = " ".join(cmd)
    # os.system(run_cmd)
    hmmscan.run(
        orfs=seqfile,
        hmmdb=hmmdb,
        outfpath=out,
        cpus=2,
        parallel=True,
        seed=42,
        force=True,
    )


if __name__ == "__main__":
    hmmdb_dir = "/Users/rees/Wisc/kwan/for_brian/complex_metagenomes/marker_annotater/test_data/hmms"
    orfs_dir = "/Users/rees/Wisc/kwan/for_brian/complex_metagenomes/marker_annotater/test_data/orfs"
    outdir = "/Users/rees/Wisc/kwan/for_brian/complex_metagenomes/marker_annotater/test_data/hmmscan"
    if not os.path.exists(outdir) or not os.path.isdir(outdir):
        os.makedirs(outdir)
    for seqfile in glob.glob(os.path.join(orfs_dir, "*.orfs.faa")):
        hmmdb_filename = os.path.basename(seqfile).replace(".orfs.faa", ".hmm")
        hmmdb = os.path.join(hmmdb_dir, hmmdb_filename)
        if not os.path.exists(hmmdb):
            continue
        outfilename = os.path.basename(seqfile).replace(".faa", ".hmmscan.tsv")
        out = os.path.join(outdir, outfilename)
        hmmdb_formatter.s(hmmdb).apply_async()
        scanner.s(seqfile, hmmdb, out).apply_async(countdown=2)


def get_clusters_geom_medians(df: pd.DataFrame, cluster_col: str = "cluster", weight_col: str='length') -> pd.DataFrame:
    """Compute each cluster's (`cluster_col`) geometric median weighted by contig length (`weight_col`)

    Parameters
    ----------
    df : pd.DataFrame
        Table containing x_1 and x_2 coordinates and `cluster_col` from embedding
    cluster_col : str, optional
        Value to use for cluster column, by default "cluster"
    weight_col : str, optional
        Column to use for weighting the geometric median computation, by default 'length'

    Returns
    -------
    pd.DataFrame
        index=range(cluster_1, cluster_n), cols=[cluster_col, x_1, x_2, termination, weighted]
        `x_1` and `x_2` correspond to the computed geometric median values corresponding to the respective cluster.
        `termination` is the reason of termination passed from the `compute_geometric_median` function
        `weighted` denotes the value that was used for weighting the cluster's geometric median (`weight_col`)

    """
    medians = []
    for cluster, dff in df.groupby(cluster_col):
        points = dff[['x_1', 'x_2']].to_numpy()
        if weight_col:
            weights = dff[weight_col].to_numpy()
        out = compute_geometric_median(points=points, weights=weights)
        median = out.median
        medians.append({cluster_col: cluster, "x_1": median[0], "x_2": median[1], "termination": out.termination, "weighted":weight_col})
    medians_df = pd.DataFrame(medians)
    return medians_df