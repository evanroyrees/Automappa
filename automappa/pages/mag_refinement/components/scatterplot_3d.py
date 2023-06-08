# -*- coding: utf-8 -*-

from typing import Dict, List

from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.components import ids

from automappa.utils.figures import (
    get_scatterplot_3d,
)


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.SCATTERPLOT_3D, "figure"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.AXES_2D_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_3D_ZAXIS_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_3D_LEGEND_TOGGLE, "value"),
            Input(ids.COLOR_BY_COLUMN_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_2D, "selectedData"),
        ],
    )
    def scatterplot_3d_figure_callback(
        sample: SampleTables,
        axes_columns: str,
        z_axis: str,
        show_legend: bool,
        color_by_col: str,
        selected_contigs: Dict[str, List[Dict[str, str]]],
    ) -> go.Figure:
        df = sample.binning.table
        color_by_col = "phylum" if color_by_col not in df.columns else color_by_col
        if not selected_contigs:
            contigs = set(df.index.tolist())
        else:
            contigs = {point["text"] for point in selected_contigs["points"]}
        # Subset DataFrame by selected contigs
        df = df[df.index.isin(contigs)]
        if color_by_col == "cluster":
            # Categoricals for binning
            df[color_by_col] = df[color_by_col].fillna("unclustered")
        else:
            # Other possible categorical columns all relate to taxonomy
            df[color_by_col] = df[color_by_col].fillna("unclassified")
        x_axis, y_axis = axes_columns.split("|")
        fig = get_scatterplot_3d(
            df=df,
            x_axis=x_axis,
            y_axis=y_axis,
            z_axis=z_axis,
            color_by_col=color_by_col,
        )
        fig.update_layout(showlegend=show_legend)
        return fig

    return html.Div(
        [
            html.Label("Figure 2: 3D Metagenome Overview"),
            dcc.Loading(
                id=ids.LOADING_SCATTERPLOT_3D,
                children=[
                    dcc.Graph(
                        id=ids.SCATTERPLOT_3D,
                        clear_on_unhover=True,
                        config={
                            "toImageButtonOptions": dict(
                                format="svg",
                                filename="figure_2_3D_metagenome_overview",
                            ),
                            "displayModeBar": True,
                            "displaylogo": False,
                        },
                    )
                ],
                type="graph",
            ),
        ]
    )
