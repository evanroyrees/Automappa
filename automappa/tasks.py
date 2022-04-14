#!/usr/bin/env python


import os
import glob
import pandas as pd

from geom_median.numpy import compute_geometric_median
from celery.utils.log import get_task_logger
from celery import Celery, chain
from celery.result import AsyncResult

from dotenv import load_dotenv

from autometa.common.external import hmmscan
from autometa.common.kmers import normalize, embed, count

load_dotenv()

CELERY_REDIS_URL = os.environ.get("CELERY_REDIS_URL")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")

queue = Celery(__name__, backend=CELERY_REDIS_URL, broker=CELERY_BROKER_URL)

logger = get_task_logger(__name__)


def get_job(job_id):
    """
    To be called from automappa web app.
    The job ID is passed and the celery job is returned.
    """
    return AsyncResult(job_id, app=queue)


# TODO: Data loader
# TODO: Create 2d-scatterplot figure
# TODO: Marker symbols
# TODO: CheckM annotation
# TODO: kmer freq. analysis pipeline
# TODO: scatterplot 2-d embedding views


@queue.task
def get_embedding(
    assembly: str, norm_method: str = "am_clr", embed_method: str = "densmap"
):
    counts = count(
        assembly=assembly,
        size=5,
        out=None,
        force=False,
        verbose=True,
        cpus=1,
    )
    norm_df = normalize(counts, method=norm_method)
    return embed(norm_df, method=embed_method, embed_dimensions=2)


# @queue.task
# def hmmdb_formatter(hmmdb) -> None:
#     hmmscan.hmmpress(hmmdb)


# @queue.task
# def scanner(seqfile, hmmdb, out) -> str:
#     # NOTE: returns outfpath
#     # cmd = [
#     #     "hmmscan",
#     #     "--cpu",
#     #     "1",
#     #     "--seed",
#     #     "42",
#     #     "--tblout",
#     #     out,
#     #     hmmdb,
#     #     seqfile
#     # ]
#     # run_cmd = " ".join(cmd)
#     # os.system(run_cmd)
#     hmmscan.run(
#         orfs=seqfile,
#         hmmdb=hmmdb,
#         outfpath=out,
#         cpus=2,
#         parallel=True,
#         seed=42,
#         force=True,
#     )


@queue.task
def get_clusters_geom_medians(
    df: pd.DataFrame, cluster_col: str = "cluster", weight_col: str = "length"
) -> pd.DataFrame:
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
        points = dff[["x_1", "x_2"]].to_numpy()
        if weight_col:
            weights = dff[weight_col].to_numpy()
        out = compute_geometric_median(points=points, weights=weights)
        median = out.median
        medians.append(
            {
                cluster_col: cluster,
                "x_1": median[0],
                "x_2": median[1],
                "termination": out.termination,
                "weighted": weight_col,
            }
        )
    medians_df = pd.DataFrame(medians)
    return medians_df


@queue.task
def get_embedding_traces_df(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Compute all embeddings for assembly...
    # 2. groupby cluster
    # 3. Extract k-mer size, norm method, embed method
    embedding_fpaths = glob.glob("data/nubbins/kmers/*5mers*am_clr.*2.tsv.gz")
    embeddings = []
    for fp in embedding_fpaths:
        df = pd.read_csv(fp, sep="\t", index_col="contig")
        basename = os.path.basename(fp)
        mers, norm_method, embed_method_dim, *__ = basename.split(".")
        match = re.match("(\w+)(\d+)", embed_method_dim)
        if match:
            embed_method, embed_dim = match.groups()
        df.rename(
            columns={
                "x_1": f"{embed_method}_x_1",
                "x_2": f"{embed_method}_x_2",
            },
            inplace=True,
        )
        embeddings.append(df)
    embeddings_df = pd.concat(embeddings, axis=1)

    df = pd.read_csv("data/nubbins/nubbins.tsv", sep="\t")
    main_df = df.drop(columns=["x_1", "x_2"]).set_index("contig").join(embeddings_df)
    embed_traces = []
    for embed_method in ["trimap", "densmap", "bhsne", "umap", "sksne"]:
        traces_df = get_scattergl_traces(
            df, f"{embed_method}_x_1", f"{embed_method}_x_2", "cluster"
        )
        traces_df.rename(columns={"trace": embed_method}, inplace=True)
        embed_traces.append(traces_df)
    embed_traces_df = pd.concat(embed_traces, axis=1)
    return embed_traces_df


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
