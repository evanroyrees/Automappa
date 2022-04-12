#!/usr/bin/env python

from typing import List, Union
import numpy as np
import pandas as pd
from dash.exceptions import PreventUpdate
from plotly import graph_objects as go

def taxonomy_sankey(df: pd.DataFrame, selected_rank: str = "species") -> go.Figure:
    ranks = ["superkingdom", "phylum", "class", "order", "family", "genus", "species"]
    n_ranks = len(ranks[: ranks.index(selected_rank)])
    dff = df[[col for col in df.columns if col in ranks]].fillna("unclassified")
    for rank in ranks:
        if rank in dff:
            dff[rank] = dff[rank].map(
                lambda x: f"{rank[0]}_{x}" if rank != "superkingdom" else f"d_{x}"
            )
    label = []
    for rank in ranks[:n_ranks]:
        label.extend(dff[rank].unique().tolist())
    source = []
    target = []
    value = []
    for rank in ranks[:n_ranks]:
        for rank_name, rank_df in dff.groupby(rank):
            source_index = label.index(rank_name)
            next_rank_i = ranks.index(rank) + 1
            if next_rank_i >= len(ranks[:n_ranks]):
                continue
            next_rank = ranks[next_rank_i]
            # all source is from label rank name index
            for rank_n in rank_df[next_rank].unique():
                target_index = label.index(rank_n)
                value_count = len(rank_df[rank_df[next_rank] == rank_n])
                label.append(source_index)
                source.append(source_index)
                target.append(target_index)
                value.append(value_count)
    return go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=8,
                    thickness=13,
                    line=dict(width=0.3),
                    label=label,
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                ),
            )
        ]
    )


def metric_boxplot(
    df: pd.DataFrame,
    metrics: List[str] = [],
    horizontal: bool = False,
    boxmean: Union[bool, str] = True,
) -> go.Figure:
    """Generate go.Figure of go.Box traces for provided `metric`.

    Parameters
    ----------
    df : pd.DataFrame
        MAG annotations dataframe
    metrics : List[str], optional
        MAG metrics to use for generating traces
    horizontal : bool, optional
        Whether to generate horizontal or vertical boxplot traces in the figure.
    boxmean : Union[bool,str], optional
        method to style mean and standard deviation or only to display quantiles with median.
        choices include False/True and 'sd'

    Returns
    -------
    go.Figure
        Figure of boxplot traces using provided parameters and aesthetics

    Raises
    ------
    PreventUpdate
        No metrics were provided to generate traces.
    """
    fig = go.Figure()
    if not metrics:
        raise PreventUpdate
    for metric in metrics:
        name = metric.replace("_", " ").title()
        if horizontal:
            trace = go.Box(x=df[metric], name=name, boxmean=boxmean)
        else:
            trace = go.Box(y=df[metric], name=name, boxmean=boxmean)
        # TODO: round to two decimal places
        # Perhaps a hovertemplate formatting issue?
        fig.add_trace(trace)
    return fig


def marker_size_scaler(x: pd.DataFrame, scale_by: str = "length") -> int:
    x_min_scaler = x[scale_by] - x[scale_by].min()
    x_max_scaler = x[scale_by].max() - x[scale_by].min()
    if not x_max_scaler:
        # Protect Division by 0
        x_ceil = np.ceil(x_min_scaler / x_max_scaler + 1)
    else:
        x_ceil = np.ceil(x_min_scaler / x_max_scaler)
    x_scaled = x_ceil * 2 + 4
    return x_scaled




def get_scatterplot_2d(
    df,
    x_axis: str = "x_1",
    y_axis: str = "x_2",
    color_by_col: str = "cluster",
) -> go.Figure:
    fig = go.Figure(
        layout=go.Layout(
            scene=dict(
                xaxis=dict(title=x_axis.title()),
                yaxis=dict(title=y_axis.title()),
            ),
            legend=dict(x=1, y=1),
            margin=dict(r=50, b=50, l=50, t=50),
            hovermode="closest",
        ),
    )
    # Hovertemplate
    x_hover_label = f"{x_axis.title()}: " + "%{x:.2f}"
    y_hover_label = f"{y_axis.title()}: " + "%{y:.2f}"
    coverage_label = "Coverage: %{customdata[0]:.2f}"
    gc_content_label = "GC%: %{customdata[1]:.2f}"
    length_label = "Length: %{customdata[2]:,} bp"
    text_hover_label = "Contig: %{text}"
    hovertemplate = "<br>".join(
        [
            text_hover_label,
            coverage_label,
            gc_content_label,
            length_label,
            x_hover_label,
            y_hover_label,
        ]
    )

    metadata_cols = ["coverage", "gc_content", "length"]
    for color_col_name in df[color_by_col].unique():
        dff = df.loc[df[color_by_col].eq(color_col_name)]
        trace = go.Scattergl(
            x=dff[x_axis],
            y=dff[y_axis],
            customdata=dff[metadata_cols],
            text=dff.index,
            mode="markers",
            opacity=0.85,
            hovertemplate=hovertemplate,
            name=color_col_name,
        )
        fig.add_trace(trace)
    fig.update_layout(legend_title_text=color_by_col.title())
    return fig


def get_scatterplot_3d(
    df,
    x_axis: str = "x_1",
    y_axis: str = "x_2",
    z_axis: str = "coverage",
    color_by_col: str = "cluster",
) -> go.Figure:
    fig = go.Figure(
        layout=go.Layout(
            scene=dict(
                xaxis=dict(title=x_axis.title()),
                yaxis=dict(title=y_axis.title()),
                zaxis=dict(title=z_axis.replace("_", " ").title()),
            ),
            legend={"x": 1, "y": 1},
            autosize=True,
            margin=dict(r=0, b=0, l=0, t=25),
            hovermode="closest",
        )
    )
    x_hover_label = f"{x_axis.title()}: " + "%{x:.2f}"
    y_hover_label = f"{y_axis.title()}: " + "%{y:.2f}"
    z_hover_label = f"{z_axis.title()}: " + "%{z:.2f}"
    text_hover_label = "Contig: %{text}"
    hovertemplate = "<br>".join(
        [text_hover_label, z_hover_label, x_hover_label, y_hover_label]
    )
    for color_by_col_val, dff in df.groupby(color_by_col):
        trace = go.Scatter3d(
            x=dff[x_axis],
            y=dff[y_axis],
            z=dff[z_axis],
            text=dff.contig,
            mode="markers",
            marker={
                "size": df.assign(normLen=marker_size_scaler)["normLen"],
                "line": {"width": 0.1, "color": "black"},
            },
            opacity=0.45,
            hoverinfo="all",
            hovertemplate=hovertemplate,
            name=color_by_col_val,
        )
        fig.add_trace(trace)
    fig.update_layout(legend_title_text=color_by_col.title())
    return fig


if __name__ == "__main__":
    pass
