#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import dcc, html
from dash_extensions.enrich import DashProxy, Input, Output
from plotly import graph_objects as go

from automappa.data.source import SampleTables
from automappa.utils.figures import (
    format_axis_title,
    get_scatterplot_2d,
)

from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.SCATTERPLOT_2D, "figure"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.KMER_SIZE_DROPDOWN, "value"),
            Input(ids.NORM_METHOD_DROPDOWN, "value"),
            Input(ids.AXES_2D_DROPDOWN, "value"),
            Input(ids.SCATTERPLOT_2D_LEGEND_TOGGLE, "value"),
            Input(ids.COLOR_BY_COLUMN_DROPDOWN, "value"),
            Input(ids.HIDE_SELECTIONS_TOGGLE, "value"),
            Input(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
        ],
        log=True,
    )
    def scatterplot_2d_figure_callback(
        sample: SampleTables,
        kmer_size_dropdown_value: int,
        norm_method_dropdown_value: str,
        axes_columns: str,
        show_legend: bool,
        color_by_col: str,
        hide_selection_toggle: bool,
        btn_clicks: int,
    ) -> go.Figure:
        # NOTE: btn_clicks is an input so this figure is updated when new refinements are saved
        # TODO: #23 refactor scatterplot callbacks
        # - Add Input("scatterplot-2d", "layout") ?
        # TODO: Refactor data retrieval/validation
        bin_df = sample.binning.table
        # TODO: Replace binning table w/coords-data
        # Replace binning table w/metagenome-annotations-data[TODO]
        # mag_cols=["length", "gc_content", "coverage"]
        markers = sample.marker_symbols.table
        if color_by_col not in bin_df.columns:
            for col in ["phylum", "class", "order", "family"]:
                if col in bin_df.columns:
                    color_by_col = col
                    break
        if color_by_col not in bin_df.columns:
            raise ValueError(
                f"No columns were found in binning-main that could be used to group traces. {color_by_col} not found in table..."
            )
        # Subset metagenome-annotations by selections iff selections have been made
        if hide_selection_toggle:
            refine_df = sample.refinements.table
            refine_cols = [col for col in refine_df.columns if "refinement" in col]
            if refine_cols:
                latest_refine_col = refine_cols.pop()
                # Retrieve only contigs that have already been refined...
                refined_contigs_index = refine_df[
                    refine_df[latest_refine_col].str.contains("refinement")
                ].index
                bin_df.drop(
                    refined_contigs_index, axis="index", inplace=True, errors="ignore"
                )
        # TODO: Refactor figure s.t. updates are applied in
        # batches for respective styling,layout,traces, etc.
        # TODO: Put figure or traces in store, get/update/select
        # based on current contig selections
        # TODO: Should check norm_method, kmer_size prior to retrieving embeddings table...
        # Add norm method and kmer_size dropdowns...
        xaxis_column, yaxis_column = axes_columns.split("|")
        if "_x_1" in xaxis_column or "_x_2" in yaxis_column:
            # TODO: Fix retrieval of axes with embeddings...
            for embeddings in sample.embeddings:
                sizemers, norm_method, __ = embeddings.name.split("-")
                kmer_size = int(sizemers.replace("mers", ""))
                if (
                    norm_method == norm_method_dropdown_value
                    and kmer_size == kmer_size_dropdown_value
                    and embeddings.exists
                ):
                    embedding_df = embeddings.table
                    bin_df = bin_df.join(embedding_df, how="left")
        else:
            for kmer in sample.kmers:
                if (
                    f"{kmer.embedding.name}_x_1" == xaxis_column
                    and f"{kmer.embedding.name}_x_2" == yaxis_column
                    and kmer.size == kmer_size_dropdown_value
                    and kmer.norm_method == norm_method_dropdown_value
                ):
                    bin_df = bin_df.join(kmer.embedding.table, how="left")
                    break

        fillnas = {
            "cluster": "unclustered",
            "superkingdom": "unclassified",
            "phylum": "unclassified",
            "class": "unclassified",
            "order": "unclassified",
            "family": "unclassified",
            "genus": "unclassified",
            "species": "unclassified",
        }
        fillna = fillnas.get(color_by_col, "unclustered")
        fig = get_scatterplot_2d(
            bin_df,
            x_axis=xaxis_column,
            y_axis=yaxis_column,
            color_by_col=color_by_col,
            fillna=fillna,
        )

        # TODO: If possible, as a separate callback do Output("scatterplot-2d", "layout")
        with fig.batch_update():
            fig.layout.xaxis.title = format_axis_title(xaxis_column)
            fig.layout.yaxis.title = format_axis_title(yaxis_column)
            fig.layout.legend.title = color_by_col.title()
            fig.layout.showlegend = show_legend

        # Update markers with symbol and size corresponding to marker count
        # TODO: If possible, as a separate callback do Output("scatterplot-2d", "traces")
        fig.for_each_trace(
            lambda trace: trace.update(
                marker_symbol=markers.symbol.loc[trace.text],
                marker_size=markers.marker_size.loc[trace.text],
            )
        )
        return fig

    return html.Div(
        [
            html.Label("Figure 1: 2D Metagenome Overview"),
            dcc.Loading(
                id=ids.LOADING_SCATTERPLOT_2D,
                children=[
                    dcc.Graph(
                        id=ids.SCATTERPLOT_2D,
                        clear_on_unhover=True,
                        config={"displayModeBar": True, "displaylogo": False},
                    )
                ],
                type="graph",
            ),
        ]
    )
