#!/usr/bin/env python

import random
from dash.exceptions import PreventUpdate
from dash import Patch
from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc, ctx
import dash_mantine_components as dmc
from typing import List

from automappa.components import ids
from automappa.pages.home.tasks.task_status_badge import set_badge_color


PENDING = "PENDING"
STARTED = "STARTED"
RETRY = "RETRY"
FAILURE = "FAILURE"
SUCCESS = "SUCCESS"


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.BADGE_TASK_STORE, "data", allow_duplicate=True),
        Input(ids.BACKGROUND_TASK_BUTTON, "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def create_task(btn: int):
        if not ctx.triggered_id == ids.BACKGROUND_TASK_BUTTON:
            raise PreventUpdate
        task_ids = Patch()
        color = random.choice(["green", "lime"])
        task = set_badge_color.delay((color,))
        task_ids.append(task.id)
        return task_ids

    @app.callback(
        Output(ids.BACKGROUND_TASK_BADGE, "color"),
        Output(ids.BADGE_TASK_STORE, "data", allow_duplicate=True),
        Input(ids.BADGE_STATUS_INTERVAL, "n_intervals"),
        State(ids.BADGE_TASK_STORE, "data"),
        prevent_initial_call=True,
    )
    def read_tasks(n_intervals: int, task_ids: List[str]) -> str:
        if not task_ids:
            raise PreventUpdate
        for task_id in task_ids:
            task = set_badge_color.AsyncResult(task_id)
            if task.status == PENDING:
                color = "orange"
            elif task.status == STARTED:
                color = "blue"
            elif task.status == RETRY:
                color = "yellow"
            elif task.status == FAILURE:
                color = "red"
            else:
                # i.e. task.status == SUCCESS
                color = task.get()
                task_ids.pop(task_ids.index(task_id))
        return color, task_ids

    @app.callback(
        Output(ids.BACKGROUND_TASK_BADGE, "children"),
        Input(ids.BADGE_STATUS_INTERVAL, "n_intervals"),
        Input(ids.BADGE_TASK_STORE, "data"),
    )
    def read_tasks_count(n_intervals: int, task_ids: List[str]) -> str:
        if not task_ids:
            text = f"0 tasks!"
        else:
            n_tasks = len(task_ids)
            text = f"{n_tasks} task" if n_tasks == 1 else f"{n_tasks} tasks"
        return text

    # NOTE: You can uncomment this callback
    # for disabling submit button when task is submitted
    @app.callback(
        Output(ids.BACKGROUND_TASK_BUTTON, "disabled"),
        Input(ids.BADGE_TASK_STORE, "data"),
    )
    def disable_task_button(task_ids: List[str]) -> bool:
        return True if task_ids else False

    return html.Div(
        [
            dcc.Store(ids.BADGE_TASK_STORE, data=[]),
            dcc.Interval(ids.BADGE_STATUS_INTERVAL, interval=500),
            dmc.Button(
                children=[dmc.Text("task button")], id=ids.BACKGROUND_TASK_BUTTON
            ),
            dmc.Badge(id=ids.BACKGROUND_TASK_BADGE),
        ]
    )
