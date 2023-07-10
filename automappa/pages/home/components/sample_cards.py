from typing import List, Optional, Protocol, Tuple, Union
import uuid
import random
from dash.exceptions import PreventUpdate
from dash import Patch
from dash_extensions.enrich import (
    DashProxy,
    html,
    Input,
    Output,
    State,
    ctx,
    MATCH,
    ALL,
)
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from automappa.components import ids


LOADER_COLORS = [
    "pink",
    "violet",
    "indigo",
    "blue",
    "lime",
    "orange",
]


class SampleCardsDataSource(Protocol):
    def get_sample_names(self) -> List[Tuple[int, str]]:
        ...

    def contig_count(self, metagenome_id: int) -> int:
        ...

    def marker_count(self, metagenome_id: int) -> int:
        ...

    def connections_count(self, metagenome_id: int) -> int:
        ...

    def create_metagenome(
        self,
        name: str,
        metagenome_fpaths: List[str],
        metagenome_is_completed: bool,
        metagenome_upload_id: uuid.UUID,
        binning_fpaths: List[str],
        binning_is_completed: bool,
        binning_upload_id: uuid.UUID,
        markers_fpaths: List[str],
        markers_is_completed: bool,
        markers_upload_id: uuid.UUID,
        connections_fpaths: Union[List[str], None] = None,
        connections_is_completed: Union[bool, None] = None,
        connections_upload_id: Union[uuid.UUID, None] = None,
    ) -> int:
        """Create Metagenome object in db

        Parameters
        ----------
        name : str
            _description_
        metagenome_fpaths : List[str]
            _description_
        metagenome_is_completed : bool
            _description_
        metagenome_upload_id : uuid.UUID
            _description_
        binning_fpaths : List[str]
            _description_
        binning_is_completed : bool
            _description_
        binning_upload_id : uuid.UUID
            _description_
        markers_fpaths : List[str]
            _description_
        markers_is_completed : bool
            _description_
        markers_upload_id : uuid.UUID
            _description_
        connections_fpaths : Union[List[str], None], optional
            _description_, by default None
        connections_is_completed : Union[bool, None], optional
            _description_, by default None
        connections_upload_id : Union[uuid.UUID, None], optional
            _description_, by default None

        Returns
        -------
        int
            Metagenome primary key (e.g. Metagenome.id)
        """
        ...


def get_badge(label: str, id: str, color: str) -> dmc.Badge:
    return dmc.Badge(label, id=id, color=color, variant="dot", size="sm")


def render(app: DashProxy, source: SampleCardsDataSource) -> html.Div:
    def new_card(metagenome_name: str, metagenome_id: Optional[int] = None) -> dmc.Card:
        connections_count = source.connections_count(metagenome_id)
        badges = [
            get_badge(
                label=ids.SAMPLE_CARD_METAGENOME_BADGE_LABEL,
                id={
                    ids.SAMPLE_CARD_INDEX: metagenome_id,
                    "type": ids.SAMPLE_CARD_METAGENOME_BADGE_TYPE,
                },
                color="lime",
            ),
            get_badge(
                label=f"{ids.SAMPLE_CARD_BINNING_BADGE_LABEL}: {source.contig_count(metagenome_id):,}",
                id={
                    ids.SAMPLE_CARD_INDEX: metagenome_id,
                    "type": ids.SAMPLE_CARD_BINNING_BADGE_TYPE,
                },
                color="lime",
            ),
            get_badge(
                label=f"{ids.SAMPLE_CARD_MARKERS_BADGE_LABEL}: {source.marker_count(metagenome_id):,}",
                id={
                    ids.SAMPLE_CARD_INDEX: metagenome_id,
                    "type": ids.SAMPLE_CARD_MARKERS_BADGE_TYPE,
                },
                color="lime",
            ),
            get_badge(
                label=ids.SAMPLE_CARD_CONNECTIONS_BADGE_LABEL
                if connections_count == 0
                else f"{ids.SAMPLE_CARD_CONNECTIONS_BADGE_LABEL}: {connections_count:,}",
                id={
                    ids.SAMPLE_CARD_INDEX: metagenome_id,
                    "type": ids.SAMPLE_CARD_CONNECTIONS_BADGE_TYPE,
                },
                color="lime" if connections_count > 0 else "red",
            ),
        ]
        return dmc.Card(
            id={ids.SAMPLE_CARD_INDEX: metagenome_id, "type": ids.SAMPLE_CARD_TYPE},
            children=[
                dmc.CardSection(
                    dmc.Group(
                        children=[
                            dmc.Text(
                                metagenome_name.replace("_", " ").title(),
                                weight=500,
                            )
                        ]
                    ),
                    withBorder=True,
                    inheritPadding=True,
                    py="xs",
                ),
                dmc.Space(h=10),
                dmc.SimpleGrid(cols=1, children=badges),
                dmc.Space(h=10),
                dmc.CardSection(dmc.Divider(variant="dashed"), withBorder=False),
                dmc.Space(h=10),
                dmc.Chip(
                    "Selected",
                    id={
                        ids.SAMPLE_CARD_INDEX: metagenome_id,
                        "type": ids.SAMPLE_CARD_CHIP_TYPE,
                    },
                    size="sm",
                    variant="outline",
                    radius="xl",
                    checked=False,
                ),
            ],
            withBorder=False,
            shadow="sm",
            radius="md",
            styles=dict(color="lime"),
        )

    @app.callback(
        Output(
            {ids.SAMPLE_CARD_INDEX: MATCH, "type": ids.SAMPLE_CARD_TYPE},
            "withBorder",
        ),
        Input(
            {ids.SAMPLE_CARD_INDEX: MATCH, "type": ids.SAMPLE_CARD_CHIP_TYPE}, "checked"
        ),
        prevent_initial_call=True,
    )
    def sample_card_selected(sample_chip_checked: bool) -> bool:
        return sample_chip_checked

    # TODO Reset all other cards when one is selected
    # @app.callback(
    #     Output(
    #         {ids.SAMPLE_CARD_INDEX: MATCH, "type": ids.SAMPLE_CARD_TYPE},
    #         "withBorder",
    #     ),
    #     Input(
    #         {ids.SAMPLE_CARD_INDEX: ALL, "type": ids.SAMPLE_CARD_CHIP_TYPE}, "checked"
    #     ),
    #     prevent_initial_call=True,
    # )
    # def sync_selected_sample_card(sample_chip_checked: bool) -> bool:
    #     return sample_chip_checked

    @app.callback(
        Output(ids.SAMPLE_CARDS_CONTAINER, "children"),
        Input(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "n_clicks"),
        Input(ids.METAGENOME_UPLOAD, "isCompleted"),
        Input(ids.BINNING_UPLOAD, "isCompleted"),
        Input(ids.MARKERS_UPLOAD, "isCompleted"),
        Input(ids.CYTOSCAPE_UPLOAD, "isCompleted"),
        State(ids.METAGENOME_UPLOAD, "fileNames"),
        State(ids.METAGENOME_UPLOAD, "upload_id"),
        State(ids.BINNING_UPLOAD, "fileNames"),
        State(ids.BINNING_UPLOAD, "upload_id"),
        State(ids.MARKERS_UPLOAD, "fileNames"),
        State(ids.MARKERS_UPLOAD, "upload_id"),
        State(ids.CYTOSCAPE_UPLOAD, "fileNames"),
        State(ids.CYTOSCAPE_UPLOAD, "upload_id"),
        State(ids.SAMPLE_NAME_TEXT_INPUT, "value"),
    )
    def add_sample_card(
        submit_btn: int,
        metagenome_is_completed: bool,
        binning_is_completed: bool,
        markers_is_completed: bool,
        connections_is_completed: bool,
        metagenome_fpaths: List[str],
        metagenome_upload_id: uuid.UUID,
        binning_fpaths: List[str],
        binning_upload_id: uuid.UUID,
        markers_fpaths: List[str],
        markers_upload_id: uuid.UUID,
        connections_fpaths: List[str],
        connections_upload_id: uuid.UUID,
        metagenome_name: str,
    ) -> List[dmc.Card]:
        if (
            not metagenome_is_completed
            or not binning_is_completed
            or not markers_is_completed
        ):
            raise PreventUpdate
        if ctx.triggered_id != ids.UPLOAD_STEPPER_SUBMIT_BUTTON:
            raise PreventUpdate

        metagenome_id = source.create_metagenome(
            name=metagenome_name,
            metagenome_fpaths=metagenome_fpaths,
            metagenome_is_completed=metagenome_is_completed,
            metagenome_upload_id=metagenome_upload_id,
            binning_fpaths=binning_fpaths,
            binning_is_completed=binning_is_completed,
            binning_upload_id=binning_upload_id,
            markers_fpaths=markers_fpaths,
            markers_is_completed=markers_is_completed,
            markers_upload_id=markers_upload_id,
            connections_fpaths=connections_fpaths,
            connections_is_completed=connections_is_completed,
            connections_upload_id=connections_upload_id,
        )
        patched_sample_cards = Patch()
        # loader_color = random.choice(LOADER_COLORS)
        # sample_card = dmc.LoadingOverlay(
        #     new_card(metagenome_name),
        #     loader=dmc.Loader(color=loader_color, size="xl", variant="oval"),
        # )
        patched_sample_cards.append(new_card(metagenome_name, metagenome_id))
        return patched_sample_cards

    # TODO Callback to select sample card for MAG-refinement
    # TODO Callback to delete sample card
    sample_cards = [
        new_card(metagenome_name=name, metagenome_id=mg_id)
        for mg_id, name in source.get_sample_names()
    ]
    return html.Div(
        dmc.SimpleGrid(
            id=ids.SAMPLE_CARDS_CONTAINER,
            children=sample_cards,
            spacing="xs",
            cols=6,
            breakpoints=[
                dict(maxWidth=1500, cols=5),
                dict(maxWidth=1200, cols=4),
                dict(maxWidth=980, cols=3),
                dict(maxWidth=755, cols=2),
                dict(maxWidth=600, cols=1),
            ],
        )
    )
