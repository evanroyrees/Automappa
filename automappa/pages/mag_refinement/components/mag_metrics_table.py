#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Literal, Optional, Protocol, Union
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html
import dash_ag_grid as dag

from automappa.components import ids


class MagMetricsTableDataSource(Protocol):
    def get_marker_overview(
        self, metagenome_id: int
    ) -> List[Dict[Literal["metric", "metric_value"], Union[str, int, float]]]:
        ...

    def get_mag_metrics(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[Dict[Literal["metric", "metric_value"], Union[str, int, float]]]:
        ...


def render(app: DashProxy, source: MagMetricsTableDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_METRICS_DATATABLE, "rowData", allow_duplicate=True),
        [
            Input(ids.METAGENOME_ID_STORE, "data"),
            Input(ids.SCATTERPLOT_2D_FIGURE, "selectedData"),
        ],
        prevent_initial_call=True,
    )
    def compute_mag_metrics(
        metagenome_id: int,
        selected_contigs: Optional[Dict[str, List[Dict[str, str]]]],
    ) -> List[Dict[Literal["metric", "metric_value"], Union[str, int, float]]]:
        headers = (
            {point["text"] for point in selected_contigs["points"]}
            if selected_contigs
            else None
        )
        row_data = source.get_mag_metrics(metagenome_id=metagenome_id, headers=headers)
        return row_data

    @app.callback(
        Output(ids.MAG_METRICS_DATATABLE, "rowData", allow_duplicate=True),
        Input(ids.METAGENOME_ID_STORE, "data"),
        prevent_initial_call="initial_duplicate",
    )
    def compute_markers_overview(
        metagenome_id: int,
    ) -> List[Dict[Literal["metric", "metric_value"], Union[str, int, float]]]:
        row_data = source.get_marker_overview(metagenome_id)
        return row_data

    GREEN = "#2FCC90"
    YELLOW = "#f2e530"
    ORANGE = "#f57600"
    MIMAG_STYLE_CONDITIONS = {
        "styleConditions": [
            # High-quality >90% complete > 95% pure
            {
                "condition": "params.data.metric == 'Completeness (%)' && params.value > 90",
                "style": {"backgroundColor": GREEN},
            },
            {
                "condition": "params.data.metric == 'Purity (%)' && params.value > 95",
                "style": {"backgroundColor": GREEN},
            },
            # Medium-quality >=50% complete > 90% pure
            {
                "condition": "params.data.metric == 'Completeness (%)' && params.value >= 50",
                "style": {"backgroundColor": YELLOW},
            },
            {
                "condition": "params.data.metric == 'Purity (%)' && params.value > 90",
                "style": {"backgroundColor": YELLOW},
            },
            # Low-quality <50% complete < 90% pure
            {
                "condition": "params.data.metric == 'Completeness (%)' && params.value < 50",
                "style": {"backgroundColor": ORANGE, "color": "white"},
            },
            {
                "condition": "params.data.metric == 'Purity (%)' && params.value < 90",
                "style": {"backgroundColor": ORANGE, "color": "white"},
            },
        ]
    }

    column_defs = [
        {"field": "metric", "headerName": "MAG Metric", "resizable": True},
        {
            "field": "metric_value",
            "headerName": "Value",
            "cellStyle": MIMAG_STYLE_CONDITIONS,
        },
    ]
    return html.Div(
        [
            html.Label("Table 1. MAG Marker Metrics"),
            dcc.Loading(
                dag.AgGrid(
                    id=ids.MAG_METRICS_DATATABLE,
                    className="ag-theme-material",
                    columnSize="responsiveSizeToFit",
                    style={"height": 600, "width": "100%"},
                    columnDefs=column_defs,
                ),
                id=ids.LOADING_MAG_METRICS_DATATABLE,
                type="dot",
                color="#646569",
            ),
        ]
    )
