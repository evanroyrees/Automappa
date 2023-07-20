from typing import Dict, List, Literal, Optional, Protocol, Tuple, Union
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
from automappa.pages.home.components import sample_card


class SampleCardsDataSource(Protocol):
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

    def remove_metagenome(self, metagenome_id: int) -> None:
        ...

    def get_metagenome_ids(self) -> List[int]:
        ...


def render(app: DashProxy, source: SampleCardsDataSource) -> html.Div:
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
        return [
            sample_card.render(source, metagenome_id=mg_id)
            for mg_id in source.get_metagenome_ids()
        ]

    @app.callback(
        Output(ids.SAMPLE_CARDS_CONTAINER, "children", allow_duplicate=True),
        Input(
            {ids.SAMPLE_CARD_INDEX: ALL, "type": ids.SAMPLE_CARD_REMOVE_BTN},
            "n_clicks",
        ),
        State({ids.SAMPLE_CARD_INDEX: ALL, "type": ids.SAMPLE_CARD_REMOVE_BTN}, "id"),
        prevent_initial_call=True,
    )
    def remove_button_clicked(
        remove_btns_clicks: List[int], remove_btn_ids: Dict[str, str]
    ) -> List[dmc.Card]:
        if not any(remove_btns_clicks):
            raise PreventUpdate
        sample_card_index = [
            i for i, n_clicks in enumerate(remove_btns_clicks) if n_clicks > 0
        ][0]
        metagenome_id = remove_btn_ids[sample_card_index].get(ids.SAMPLE_CARD_INDEX)
        source.remove_metagenome(metagenome_id)
        return [
            sample_card.render(source, metagenome_id=mg_id)
            for mg_id in source.get_metagenome_ids()
        ]

    @app.callback(
        Output(ids.SAMPLE_CARDS_CONTAINER, "children", allow_duplicate=True),
        Input(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def get_sample_cards(submit_btn: int) -> List[dmc.Card]:
        return [
            sample_card.render(source, metagenome_id=mg_id)
            for mg_id in source.get_metagenome_ids()
        ]

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
