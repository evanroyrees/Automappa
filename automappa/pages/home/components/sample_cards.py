from typing import List, Optional, Protocol, Tuple, Union
import uuid
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (
    DashProxy,
    html,
    Input,
    Output,
    State,
    dcc,
    ctx,
    MATCH,
    ALL,
)
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from celery.result import GroupResult, AsyncResult

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
    def create_metagenome(
        self,
        name: str,
        metagenome_fpath: str,
        binning_fpath: str,
        markers_fpath: str,
        connections_fpath: Optional[str] = None,
    ) -> Tuple[str, int]:
        """Create Metagenome object in db

        Returns
        -------
        int
            Metagenome primary key (e.g. Metagenome.id)
        """
        ...

    def preprocess_metagenome(
        self,
        name: str,
        metagenome_fpath: str,
        binning_fpath: str,
        markers_fpath: str,
        connections_fpath: Optional[str] = None,
    ) -> GroupResult:
        """Create Metagenome object in db

        Returns
        -------
        AsyncResult
            Celery AsyncResult from task canvas preprocess metagenome pipeline
        """
        ...

    def get_preprocess_metagenome_tasks(
        self, task_ids: List[str]
    ) -> List[Tuple[str, AsyncResult]]:
        ...

    def get_metagenome_ids(self) -> List[int]:
        ...

    def contig_count(self, metagenome_id: int) -> int:
        ...

    def marker_count(self, metagenome_id: int) -> int:
        ...

    def get_metagenome_name(self, metagenome_id: int) -> str:
        """Get Metagenome.name where Metagenome.id == metagenome_id"""
        ...

    def get_approximate_marker_sets(self, metagenome_id: int) -> int:
        ...

    def get_mimag_counts(self, metagenome_id: int) -> Tuple[int, int, int]:
        ...

    def get_refinements_count(self, metagenome_id: int, initial: bool = False) -> int:
        """Get Refinement count where Refinement.metagenome_id == metagenome_id

        Providing `initial` will add where(Refinement.initial_refinement == True)
        otherwise will omit this filter and retrieve all.
        """
        ...

    def get_refined_contig_count(self, metagenome_id: int) -> int:
        ...

    def connections_count(self, metagenome_id: int) -> int:
        ...


def get_badge(label: str, id: dict[str, Union[str, int]], color: str) -> dmc.Badge:
    return dmc.Badge(label, id=id, color=color, variant="dot", size="sm")


def render(app: DashProxy, source: SampleCardsDataSource) -> html.Div:
    def new_card(metagenome_id: int) -> dmc.Card:
        connections_count = source.connections_count(metagenome_id)
        metagenome_badge = get_badge(
            label=ids.SAMPLE_CARD_METAGENOME_BADGE_LABEL,
            id={
                ids.SAMPLE_CARD_INDEX: metagenome_id,
                "type": ids.SAMPLE_CARD_METAGENOME_BADGE_TYPE,
            },
            color="lime",
        )
        binning_badge = get_badge(
            label=f"{ids.SAMPLE_CARD_BINNING_BADGE_LABEL}: {source.contig_count(metagenome_id):,}",
            id={
                ids.SAMPLE_CARD_INDEX: metagenome_id,
                "type": ids.SAMPLE_CARD_BINNING_BADGE_TYPE,
            },
            color="lime",
        )
        marker_badge = get_badge(
            label=f"{ids.SAMPLE_CARD_MARKERS_BADGE_LABEL}: {source.marker_count(metagenome_id):,} (approx. {source.get_approximate_marker_sets(metagenome_id)} sets)",
            id={
                ids.SAMPLE_CARD_INDEX: metagenome_id,
                "type": ids.SAMPLE_CARD_MARKERS_BADGE_TYPE,
            },
            color="lime",
        )
        connections_badge = get_badge(
            label=ids.SAMPLE_CARD_CONNECTIONS_BADGE_LABEL
            if connections_count == 0
            else f"{ids.SAMPLE_CARD_CONNECTIONS_BADGE_LABEL}: {connections_count:,}",
            id={
                ids.SAMPLE_CARD_INDEX: metagenome_id,
                "type": ids.SAMPLE_CARD_CONNECTIONS_BADGE_TYPE,
            },
            color="lime" if connections_count > 0 else "red",
        )
        badges = [
            metagenome_badge,
            binning_badge,
            marker_badge,
            connections_badge,
        ]
        return dmc.Card(
            id={ids.SAMPLE_CARD_INDEX: metagenome_id, "type": ids.SAMPLE_CARD_TYPE},
            children=[
                dmc.CardSection(
                    dmc.Group(
                        dmc.Text(
                            source.get_metagenome_name(metagenome_id)
                            .replace("_", " ")
                            .title(),
                            weight=500,
                        ),
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

    @app.callback(
        Output(ids.TASK_ID_STORE, "data", allow_duplicate=True),
        Input(ids.METAGENOME_UPLOAD_STORE, "data"),
        Input(ids.BINNING_MAIN_UPLOAD_STORE, "data"),
        Input(ids.MARKERS_UPLOAD_STORE, "data"),
        Input(ids.CYTOSCAPE_STORE, "data"),
        Input(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "n_clicks"),
        State(ids.SAMPLE_NAME_TEXT_INPUT, "value"),
        prevent_initial_call="initial_duplicate",
    )
    def submit_sample_ingestion_task(
        metagenome_fpath: str,
        binning_fpath: str,
        marker_fpath: str,
        connection_fpath: Union[str, None],
        submit_btn: int,
        metagenome_name: str,
    ) -> List[str]:
        if not ctx.triggered_id == ids.UPLOAD_STEPPER_SUBMIT_BUTTON:
            raise PreventUpdate
        group_result = source.preprocess_metagenome(
            metagenome_name,
            metagenome_fpath,
            binning_fpath,
            marker_fpath,
            connection_fpath,
        )
        task_ids = [group_result.parent.id] + [task.id for task in group_result.results]
        return task_ids

    @app.callback(
        Output(ids.BACKGROUND_TASK_DIV, "children"),
        Output(ids.TASK_ID_STORE, "data", allow_duplicate=True),
        Input(ids.BACKGROUND_TASK_INTERVAL, "n_intervals"),
        State(ids.TASK_ID_STORE, "data"),
        prevent_initial_call=True,
    )
    def notify_task_progress(
        n_intervals: int, task_ids: List[str]
    ) -> Tuple[List[dmc.Notification], List[str]]:
        notifications = []
        if not task_ids:
            raise PreventUpdate
        tasks = source.get_preprocess_metagenome_tasks(task_ids)
        n_tasks = len(tasks)
        tasks_completed = 0
        for task_name, task in tasks:
            if task.status in {
                "PENDING",
                "RETRY",
            }:
                loading = True
                color = "orange"
                autoclose = False
                action = "show"
                icon = DashIconify(icon="la:running")
            elif task.status == "RECEIVED":
                loading = True
                color = "blue"
                autoclose = False
                action = "update"
                icon = DashIconify(icon="la:running")
            elif task.status == "STARTED":
                loading = True
                color = "green"
                autoclose = False
                action = "update"
                icon = DashIconify(icon="ooui:error", color="red")
            elif task.status == "FAILURE" or task.status == "REVOKED":
                loading = False
                color = "red"
                autoclose = 15000
                action = "update"
                icon = DashIconify(icon="ooui:error", color="red")
            else:
                # task.status == "SUCCESS"
                loading = False
                color = "green"
                autoclose = 15000
                action = "update"
                icon = DashIconify(icon="akar-icons:circle-check")
                # Forget task upon success...
                # otherwise keep in tasks list
                tasks_completed += 1

            notification = dmc.Notification(
                id={ids.NOTIFICATION_TASK_ID: task.id},
                title=f"Task: {task_name}",
                message=f"pre-processing status: {task.status}",
                loading=loading,
                color=color,
                action=action,
                autoClose=autoclose,
                disallowClose=False,
                icon=icon,
            )
            notifications.append(notification)

        if tasks_completed == n_tasks:
            for name, task in tasks:
                task.forget()
                task_ids.pop(task_ids.index(task.id))
            for notification in notifications:
                notification.action = "update"
        return notifications, task_ids

    @app.callback(
        Output(ids.SAMPLE_CARDS_CONTAINER, "children", allow_duplicate=True),
        Input(ids.TASK_ID_STORE, "data"),
        prevent_initial_call=True,
    )
    def get_sample_cards(task_ids: List[str]) -> List[dmc.Card]:
        if task_ids:
            raise PreventUpdate
        return [new_card(metagenome_id=mg_id) for mg_id in source.get_metagenome_ids()]

    @app.callback(
        Output(ids.SAMPLE_CARDS_CONTAINER, "children", allow_duplicate=True),
        Input(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def get_sample_cards(submit_btn: int) -> List[dmc.Card]:
        return [new_card(metagenome_id=mg_id) for mg_id in source.get_metagenome_ids()]

    # TODO Callback to delete sample card
    return html.Div(
        [
            dcc.Interval(id=ids.BACKGROUND_TASK_INTERVAL, interval=3000),
            html.Div(id=ids.BACKGROUND_TASK_DIV),
            dmc.SimpleGrid(
                id=ids.SAMPLE_CARDS_CONTAINER,
                spacing="xs",
                cols=6,
                breakpoints=[
                    dict(maxWidth=1500, cols=5),
                    dict(maxWidth=1200, cols=4),
                    dict(maxWidth=980, cols=3),
                    dict(maxWidth=755, cols=2),
                    dict(maxWidth=600, cols=1),
                ],
            ),
        ]
    )
