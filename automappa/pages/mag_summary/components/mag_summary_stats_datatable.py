# -*- coding: utf-8 -*-
from typing import Protocol, List, Union, Literal, Dict
import dash_ag_grid as dag
from dash_extensions.enrich import DashProxy, Input, Output, dcc, html

from automappa.components import ids


class SummaryStatsTableDataSource(Protocol):
    def get_mag_stats_summary_row_data(
        self, metagenome_id: int
    ) -> List[
        Dict[
            Literal[
                "refinement_id",
                "refinement_label",
                "length_sum_kbp",
                "completeness",
                "purity",
                "contig_count",
            ],
            Union[str, int, float],
        ]
    ]:
        ...


def render(app: DashProxy, source: SummaryStatsTableDataSource) -> html.Div:
    @app.callback(
        Output(ids.MAG_SUMMARY_STATS_DATATABLE, "rowData"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def mag_summary_stats_datatable_callback(
        metagenome_id: int,
    ) -> List[
        Dict[
            Literal[
                "refinement_id",
                "refinement_label",
                "length_sum_kbp",
                "completeness",
                "purity",
                "contig_count",
            ],
            Union[str, int, float],
        ]
    ]:
        row_data = source.get_mag_stats_summary_row_data(metagenome_id)
        return row_data

    GREEN = "#2FCC90"
    YELLOW = "#f2e530"
    ORANGE = "#f57600"
    MIMAG_STYLE_CONDITIONS = {
        "styleConditions": [
            # High-quality >90% complete > 95% pure
            {
                "condition": "params.data.completeness == 'Completeness (%)' && params.value > 90",
                "style": {"backgroundColor": GREEN},
            },
            {
                "condition": "params.data.purity == 'Purity (%)' && params.value > 95",
                "style": {"backgroundColor": GREEN},
            },
            # Medium-quality >=50% complete > 90% pure
            {
                "condition": "params.data.completeness == 'Completeness (%)' && params.value >= 50",
                "style": {"backgroundColor": YELLOW},
            },
            {
                "condition": "params.data.purity == 'Purity (%)' && params.value > 90",
                "style": {"backgroundColor": YELLOW},
            },
            # Low-quality <50% complete < 90% pure
            {
                "condition": "params.data.completeness == 'Completeness (%)' && params.value < 50",
                "style": {"backgroundColor": ORANGE, "color": "white"},
            },
            {
                "condition": "params.data.purity == 'Purity (%)' && params.value < 90",
                "style": {"backgroundColor": ORANGE, "color": "white"},
            },
        ]
    }

    column_defs = [
        {"field": "refinement_id", "headerName": "Refinement Id", "resizable": True},
        {
            "field": "refinement_label",
            "headerName": "Refinement Label",
            "resizable": True,
        },
        {
            "field": "length_sum_kbp",
            "headerName": "Length Sum (kbp)",
            "resizable": True,
        },
        {"field": "completeness", "headerName": "Completeness (%)", "resizable": True},
        {"field": "purity", "headerName": "Purity (%)", "resizable": True},
        {
            "field": "contig_count",
            "headerName": "Contig Count",
            "cellStyle": MIMAG_STYLE_CONDITIONS,
        },
    ]

    return html.Div(
        [
            html.Label("Table 1. MAGs Summary"),
            dcc.Loading(
                dag.AgGrid(
                    id=ids.MAG_SUMMARY_STATS_DATATABLE,
                    className="ag-theme-material",
                    columnSize="responsiveSizeToFit",
                    style={"height": 600, "width": "100%"},
                    columnDefs=column_defs,
                ),
                id=ids.LOADING_MAG_SUMMARY_STATS_DATATABLE,
                type="circle",
                color="#646569",
            ),
        ]
    )
