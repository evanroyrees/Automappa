from typing import Protocol, Tuple
from dash_extensions.enrich import DashProxy, Output, Input, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from automappa.components import ids


class CoverageRangeSliderDataSource(Protocol):
    def get_coverage_min_max_values(self, metagenome_id: int) -> Tuple[float, float]:
        ...


def render(app: DashProxy, source: CoverageRangeSliderDataSource) -> html.Div:
    @app.callback(
        Output(ids.COVERAGE_RANGE_SLIDER, "max"),
        Output(ids.COVERAGE_RANGE_SLIDER, "value"),
        Input(ids.METAGENOME_ID_STORE, "data"),
    )
    def update_slider_range(
        metagenome_id: int,
    ) -> Tuple[float, float, Tuple[float, float]]:
        min_cov, max_cov = source.get_coverage_min_max_values(metagenome_id)
        min_cov = round(min_cov, 2)
        max_cov = round(max_cov, 2)
        return max_cov, (min_cov, max_cov)

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
