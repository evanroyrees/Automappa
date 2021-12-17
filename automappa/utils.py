#!/usr/bin/env python

import pandas as pd


def get_cluster_marker_counts(
    df: pd.DataFrame, markers_df: pd.DataFrame
) -> pd.DataFrame:
    marker_cols = [col for col in markers_df.columns if "PF" in col or "TIGR" in col]
    marke = df.join(markers_df).groupby("cluster")[marker_cols]
    return marke.sum()


def get_contig_marker_counts(
    bin_df: pd.DataFrame, markers_df: pd.DataFrame, marker_count_range_end: int = 7
) -> pd.DataFrame:
    df = bin_df.join(markers_df).fillna(0).copy()
    df = df[markers_df.columns.tolist()]
    ## Get copy number marker counts
    dfs = []
    marker_counts_range = list(
        range(marker_count_range_end + 1)
    )  # range(start=inclusive, end=exclusive)
    for marker_count in marker_counts_range:
        # Check if last in the list of marker_counts_range to apply df.ge(...) instead of df.eq(...)
        if marker_count + 1 == len(marker_counts_range):
            marker_count_contig_idx = df.loc[
                df.sum(axis=1).ge(marker_count)
            ].index.unique()
        else:
            marker_count_contig_idx = df.loc[
                df.sum(axis=1).eq(marker_count)
            ].index.unique()
        if marker_count_contig_idx.empty:
            continue
        count_df = pd.DataFrame(marker_count_contig_idx)
        count_df["marker_count"] = marker_count
        dfs.append(count_df)
    return pd.concat(dfs).set_index("contig")


def convert_marker_counts_to_marker_symbols(df: pd.DataFrame) -> pd.DataFrame:
    # https://plotly.com/python/marker-style/
    symbols = {
        0: "circle",
        1: "square",
        2: "diamond",
        3: "triangle-up",
        4: "x",
        5: "pentagon",
        6: "hexagon2",
        7: "hexagram",
    }
    # circle = 0
    # circle-dot = 1
    # circle-cross = 2
    # triangle-up = 3
    # square = 4
    # pentagon = 5
    # hexagon2 = 6
    # hexagram-dot = 7+
    df["symbol"] = df.marker_count.map(lambda count: symbols.get(count))
    return df
