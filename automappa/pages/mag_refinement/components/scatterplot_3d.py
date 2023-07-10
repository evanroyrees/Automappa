# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Optional, Protocol, Union
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
from plotly import graph_objects as go

from automappa.components import ids

from automappa.utils.figures import format_axis_title


class Scatterplot3dDataSource(Protocol):
    def get_scaterplot3d_records(
        self,
        metagenome_id: int,
        x_axis: str,
        y_axis: str,
        z_axis: str,
        color_by_col: str,
        headers: Optional[List[str]],
    ) -> Dict[
        str,
        Dict[Literal["x", "y", "z", "marker_size", "text"], List[Union[float, str]]],
    ]:
        ...


def get_hovertemplate(x_axis_label: str, y_axis_label: str, z_axis_label: str) -> str:
    x_hover_label = f"{x_axis_label}: " + "%{x:.2f}"
    y_hover_label = f"{y_axis_label}: " + "%{y:.2f}"
    z_hover_label = f"{z_axis_label}: " + "%{z:.2f}"
    text_hover_label = "Contig: %{text}"
    hovertemplate = "<br>".join(
        [text_hover_label, z_hover_label, x_hover_label, y_hover_label]
    )
    return hovertemplate


def get_traces(
    data: Dict[
        str,
        Dict[Literal["x", "y", "z", "marker_size", "text"], List[Union[float, str]]],
    ],
    hovertemplate: Optional[str] = "Contig: %{text}",
) -> List[go.Scatter3d]:
    return [
        go.Scatter3d(
            x=trace["x"],
            y=trace["y"],
            z=trace["z"],
            text=trace["text"],  # contig header
            name=name,  # groupby (color by column) value
            mode="markers",
            marker=dict(size=trace["marker_size"], line=dict(width=0.1, color="black")),
            opacity=0.45,
            hoverinfo="all",
            hovertemplate=hovertemplate,
        )
        for name, trace in data.items()
    ]


def render(app: DashProxy, source: Scatterplot3dDataSource) -> html.Div:
    # @app.callback(
    #     Output(ids.SCATTERPLOT_3D, "figure", allow_duplicate=True),
    #     Input(ids.SCATTERPLOT_3D_LEGEND_TOGGLE, "checked"),
    #     prevent_initial_call=True,
    # )
    # def toggle_legend(legend_switch_checked: bool) -> go.Figure:
    #     fig = Patch()
    #     fig.layout.showlegend = legend_switch_checked
    #     # fig["data"][0]["showlegend"] = legend_switch_checked
    #     return fig

    @app.callback(
        Output(ids.SCATTERPLOT_3D, "figure"),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.AXES_2D_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_3D_LEGEND_TOGGLE, "checked"),
            Input(ids.COLOR_BY_COLUMN_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
        ],
    )
    def scatterplot_3d_figure_callback(
        metagenome_id: int,
        axes_columns: str,
        z_axis: str,
        show_legend: bool,
        color_by_col: str,
        selected_contigs: Dict[str, List[Dict[str, str]]],
    ) -> go.Figure:
        headers = (
            {point["text"] for point in selected_contigs["points"]}
            if selected_contigs
            else None
        )
        x_axis, y_axis = axes_columns.split("|")
        traces_data = source.get_scaterplot3d_records(
            metagenome_id=metagenome_id,
            x_axis=x_axis,
            y_axis=y_axis,
            z_axis=z_axis,
            color_by_col=color_by_col,
            headers=headers,
        )
        x_axis_title, y_axis_title, z_axis_title, color_by_col_title = map(
            format_axis_title, [x_axis, y_axis, z_axis, color_by_col]
        )
        hovertemplate = get_hovertemplate(x_axis_title, y_axis_title, z_axis_title)
        traces = get_traces(traces_data, hovertemplate)
        legend = go.layout.Legend(
            title=color_by_col_title, x=1, y=1, visible=show_legend
        )
        layout = go.Layout(
            legend=legend,
            scene=dict(
                xaxis=dict(title=x_axis_title),
                yaxis=dict(title=y_axis_title),
                zaxis=dict(title=z_axis_title),
            ),
            autosize=True,
            margin=dict(r=0, b=0, l=0, t=25),
            hovermode="closest",
        )
        fig = go.Figure(data=traces, layout=layout)
        return fig

    graph_config = {
        "toImageButtonOptions": dict(
            format="svg",
            filename="mag-refinement-scatterplot3d-figure",
        ),
        "displayModeBar": True,
        "displaylogo": False,
    }
    return html.Div(
        [
            html.Label("Figure 2: 3D Metagenome Overview"),
            dcc.Loading(
                dcc.Graph(
                    id=ids.SCATTERPLOT_3D,
                    clear_on_unhover=True,
                    config=graph_config,
                ),
                id=ids.LOADING_SCATTERPLOT_3D,
                type="graph",
            ),
        ]
    )
