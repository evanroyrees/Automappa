#!/usr/bin/env python

import glob
import os
import re

# from autometa.common.kmers import count, normalize, embed, load
import pandas as pd
from plotly import graph_objects as go

from automappa.utils.figures import get_scattergl_traces


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
        main_df, f"{embed_method}_x_1", f"{embed_method}_x_2", "cluster"
    )
    traces_df.rename(columns={"trace": embed_method}, inplace=True)
    embed_traces.append(traces_df)

traces = pd.concat(embed_traces, axis=1)

fig = go.Figure()
fig.add_traces(traces.umap.tolist())
# Update according to selected embed_method...
embed_method = "densmap"
fig.for_each_trace(lambda trace: trace.update(traces.loc[trace.name, embed_method]))
embed_method = "trimap"
fig.for_each_trace(lambda trace: trace.update(traces.loc[trace.name, embed_method]))
embed_method = "umap"
fig.for_each_trace(lambda trace: trace.update(traces.loc[trace.name, embed_method]))
embed_method = "sksne"
fig.for_each_trace(lambda trace: trace.update(traces.loc[trace.name, embed_method]))
embed_method = "bhsne"
fig.for_each_trace(lambda trace: trace.update(traces.loc[trace.name, embed_method]))
