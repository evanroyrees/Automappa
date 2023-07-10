#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Optional, Protocol, Tuple, Union
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
from plotly import graph_objects as go

from automappa.utils.figures import (
    format_axis_title,
    get_scatterplot_2d,
)

from automappa.components import ids


class Scatterplot2dDataSource(Protocol):
    def get_scatterplot2d_records(
        self,
        metagenome_id: int,
        x_axis: str,
        y_axis: str,
        color_by_col: str,
        headers: Optional[List[str]],
    ) -> Dict[
        Literal["x", "y", "marker_symbol", "marker_size", "text", "customdata"],
        List[Union[float, str, Tuple[float, float, int]]],
    ]:
        ...


def get_hovertemplate(x_axis: str, y_axis: str) -> str:
    # Hovertemplate
    x_hover_title = format_axis_title(x_axis)
    y_hover_title = format_axis_title(y_axis)
    text_hover_label = "Contig: %{text}"
    coverage_label = "Coverage: %{customdata[0]:.2f}"
    gc_content_label = "GC%: %{customdata[1]:.2f}"
    length_label = "Length: %{customdata[2]:,} bp"
    x_hover_label = f"{x_hover_title}: " + "%{x:.2f}"
    y_hover_label = f"{y_hover_title}: " + "%{y:.2f}"
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
    return hovertemplate


def get_traces(
    data: Dict[
        str,
        Dict[
            Literal[
                "x", "y", "z", "marker_size", "marker_symbol", "text", "customdata"
            ],
            List[Union[float, str, Tuple[float, float, int]]],
        ],
    ],
    hovertemplate: Optional[str] = "Contig: %{text}",
) -> List[go.Scattergl]:
    return [
        go.Scattergl(
            x=trace["x"],
            y=trace["y"],
            text=trace["text"],  # contig header
            name=name,  # groupby (color by column) value
            mode="markers",
            marker=dict(
                size=trace["marker_size"],
                line=dict(width=0.1, color="black"),
                symbol=trace["marker_symbol"],
            ),
            customdata=trace["customdata"],
            opacity=0.45,
            hoverinfo="all",
            hovertemplate=hovertemplate,
        )
        for name, trace in data.items()
    ]


def render(app: DashProxy, source: Scatterplot2dDataSource) -> html.Div:
    @app.callback(
        Output(ids.SCATTERPLOT_2D_FIGURE, "figure"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.KMER_SIZE_DROPDOWN, "value"),
            Input(ids.NORM_METHOD_DROPDOWN, "value"),
            Input(ids.AXES_2D_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_2D_LEGEND_TOGGLE, "checked"),
            Input(ids.COLOR_BY_COLUMN_DROPDOWN, "value"),
            Input(ids.HIDE_SELECTIONS_TOGGLE, "checked"),
            Input(ids.COVERAGE_RANGE_SLIDER, "value"),
            Input(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        ],
    )
    def scatterplot_2d_figure_callback(
        metagenome_id: int,
        kmer_size_dropdown_value: int,
        norm_method_dropdown_value: str,
        axes_columns: str,
        show_legend: bool,
        color_by_col: str,
        hide_selection_toggle: bool,
        coverage_range: Tuple[float, float],
        btn_clicks: int,
    ) -> go.Figure:
        # NOTE: btn_clicks is an input so this figure is updated when new refinements are saved
        # data:
        # - data.x_axis # continuous values
        # - data.y_axis # continuous values
        # - data.text # Contig.header
        # - data.groupby_value # Categoricals
        # - data.marker_size
        # - data.marker_symbol
        # - data.customdata i.e. List[Tuple(coverage, gc_content, length)]

        # callback to subset based on coverage slider
        # min_coverage, max_coverage = coverage_range
        x_axis, y_axis = axes_columns.split("|")
        hovertemplate = get_hovertemplate(x_axis, y_axis)

        records = source.get_scatterplot2d_records(
            metagenome_id=metagenome_id,
            x_axis=x_axis,
            y_axis=y_axis,
            color_by_col=color_by_col,
        )

        traces = get_traces(records, hovertemplate=hovertemplate)
        RIGHT_MARGIN = 20
        LEFT_MARGIN = 20
        BOTTOM_MARGIN = 20
        TOP_MARGIN = 20
        legend = go.layout.Legend(visible=show_legend, x=1, y=1)
        layout = go.Layout(
            legend=legend,
            margin=dict(r=RIGHT_MARGIN, b=BOTTOM_MARGIN, l=LEFT_MARGIN, t=TOP_MARGIN),
            hovermode="closest",
            clickmode="event+select",
            height=600,
        )
        fig = go.Figure(data=traces, layout=layout)
        return fig

    # fig = go.Figure(id=ids.SCATTERPLOT_2D_FIGURE)

    return html.Div(
        [
            html.Label("Figure 1: 2D Metagenome Overview"),
            dcc.Loading(
                dcc.Graph(
                    id=ids.SCATTERPLOT_2D_FIGURE,
                    clear_on_unhover=True,
                    config={"displayModeBar": True, "displaylogo": False},
                ),
                id=ids.LOADING_SCATTERPLOT_2D,
                type="graph",
            ),
        ]
    )
