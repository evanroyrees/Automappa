#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
from typing import Dict, List
from dash_extensions.enrich import DashProxy, dcc, html, Input, Output
from automappa.components import ids
from automappa.data.source import SampleTables


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.AXES_2D_DROPDOWN, "options"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
        Input(ids.KMER_SIZE_DROPDOWN, "value"),
        Input(ids.NORM_METHOD_DROPDOWN, "value"),
    )
    def axes_2d_options_callback(
        sample: SampleTables,
        kmer_size_dropdown_value: int,
        norm_method_dropdown_value: str,
    ) -> List[Dict[str, str]]:
        binning_df = sample.binning.table
        binning_combinations = [
            {
                "label": " vs. ".join(
                    [x_axis.title().replace("_", " "), y_axis.title().replace("_", " ")]
                ),
                "value": "|".join([x_axis, y_axis]),
                "disabled": False,
            }
            for x_axis, y_axis in itertools.combinations(
                binning_df.select_dtypes({"float64", "int64"}).columns, 2
            )
            if x_axis not in {"completeness", "purity", "taxid"}
            and y_axis not in {"completeness", "purity", "taxid"}
        ]
        embeddings = [
            {
                "label": kmer.embedding.name,
                "value": f"{kmer.embedding.name}_x_1|{kmer.embedding.name}_x_2",
                "disabled": not kmer.embedding.exists,
            }
            for kmer in sample.kmers
            if kmer.size == kmer_size_dropdown_value
            and kmer.norm_method == norm_method_dropdown_value
        ]
        return binning_combinations + embeddings

    return html.Div(
        [
            html.Label("Axes:"),
            dcc.Dropdown(
                id=ids.AXES_2D_DROPDOWN,
                value=ids.AXES_2D_DROPDOWN_VALUE_DEFAULT,
                clearable=False,
            ),
        ]
    )
