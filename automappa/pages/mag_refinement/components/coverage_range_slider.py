from typing import Tuple
from dash_extensions.enrich import DashProxy, Output, Input, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from automappa.components import ids
from automappa.data.source import SampleTables


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.COVERAGE_RANGE_SLIDER, "max"),
        Output(ids.COVERAGE_RANGE_SLIDER, "value"),
        Output(ids.COVERAGE_RANGE_SLIDER, "marks"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
    )
    def update_slider_range(
        sample: SampleTables,
    ) -> Tuple[float, float, Tuple[float, float]]:
        df = sample.binning.table
        minimum = df.coverage.round().astype(int).min()
        max = df.coverage.round().astype(int).max()
        marks = [
            {"value": mark, "label": f"{mark:,}x"}
            for mark in df.coverage.quantile([0, 0.25, 0.5, 0.75, 1])
            .round()
            .astype(int)
            .values
        ]
        return max, (minimum, max), marks

    return html.Div(
        [
            dmc.Text("Coverage range slider"),
            dmc.Space(h=30),
            dmc.LoadingOverlay(
                dmc.RangeSlider(
                    min=0,
                    showLabelOnHover=True,
                    labelTransition="fade",
                    labelTransitionDuration=1000,  # in ms
                    color="gray",
                    size="lg",
                    thumbFromLabel="cov",
                    thumbSize=35,
                    thumbChildren=DashIconify(icon="iconamoon:sign-x-light", width=25),
                    id=ids.COVERAGE_RANGE_SLIDER,
                ),
                loaderProps=dict(
                    variant="oval",
                    color="dark",
                    size="sm",
                ),
            ),
            dmc.Space(h=30),
        ]
    )
