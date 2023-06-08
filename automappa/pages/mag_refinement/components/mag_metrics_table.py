#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List

from dash.dash_table import DataTable
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
import pandas as pd


from automappa.data.source import SampleTables
from automappa.components import ids


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.MAG_METRICS_DATATABLE, "children"),
        [
            Input(ids.SELECTED_TABLES_STORE, "data"),
            Input(ids.SCATTERPLOT_2D, "selectedData"),
        ],
    )
    def update_mag_metrics_datatable_callback(
        sample: SampleTables,
        selected_contigs: Dict[str, List[Dict[str, str]]],
    ) -> DataTable:
        markers_df = sample.markers.table
        if selected_contigs:
            contigs = {point["text"] for point in selected_contigs["points"]}
            selected_contigs_count = len(contigs)
            markers_df = markers_df.loc[markers_df.index.isin(contigs)]

        expected_markers_count = markers_df.shape[1]

        pfam_counts = markers_df.sum()
        if pfam_counts[pfam_counts.ge(1)].empty:
            total_markers = 0
            single_copy_marker_count = 0
            markers_present_count = 0
            redundant_markers_count = 0
            marker_set_count = 0
            completeness = "NA"
            purity = "NA"
        else:
            total_markers = pfam_counts.sum()
            single_copy_marker_count = pfam_counts.eq(1).sum()
            markers_present_count = pfam_counts.ge(1).sum()
            redundant_markers_count = pfam_counts.gt(1).sum()
            completeness = markers_present_count / expected_markers_count * 100
            purity = single_copy_marker_count / markers_present_count * 100
            marker_set_count = total_markers / expected_markers_count

        marker_contig_count = markers_df.sum(axis=1).ge(1).sum()
        single_marker_contig_count = markers_df.sum(axis=1).eq(1).sum()
        multi_marker_contig_count = markers_df.sum(axis=1).gt(1).sum()
        metrics_data = {
            "Expected Markers": expected_markers_count,
            "Total Markers": total_markers,
            "Redundant-Markers": redundant_markers_count,
            "Markers Count": markers_present_count,
            "Marker Sets (Total / Expected)": marker_set_count,
            "Marker-Containing Contigs": marker_contig_count,
            "Multi-Marker Contigs": multi_marker_contig_count,
            "Single-Marker Contigs": single_marker_contig_count,
        }
        if selected_contigs:
            selection_metrics = {
                "Contigs": selected_contigs_count,
                "Completeness (%)": completeness,
                "Purity (%)": purity,
            }
            selection_metrics.update(metrics_data)
            # Adding this extra step b/c to keep selection metrics at top of the table...
            metrics_data = selection_metrics

        metrics_df = pd.DataFrame([metrics_data]).T
        metrics_df.rename(columns={0: "Value"}, inplace=True)
        metrics_df.index.name = "MAG Metric"
        metrics_df.reset_index(inplace=True)
        metrics_df = metrics_df.round(2)
        return DataTable(
            data=metrics_df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in metrics_df.columns],
            style_cell={
                "height": "auto",
                # all three widths are needed
                "minWidth": "20px",
                "width": "20px",
                "maxWidth": "20px",
                "whiteSpace": "normal",
                "textAlign": "center",
            },
            # TODO: style completeness and purity cells to MIMAG standards as mentioned above
        )

    return html.Div(
        [
            html.Label("Table 1. MAG Marker Metrics"),
            dcc.Loading(
                id=ids.LOADING_MAG_METRICS_DATATABLE,
                children=[html.Div(id=ids.MAG_METRICS_DATATABLE)],
                type="dot",
                color="#646569",
            ),
        ]
    )
