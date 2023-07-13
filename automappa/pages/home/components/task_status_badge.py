#!/usr/bin/env python

import random
from dash.exceptions import PreventUpdate
from dash import Patch
from celery import Celery
from celery.result import AsyncResult
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


def render(app: DashProxy, source, queue: Celery) -> html.Div:
    @app.callback(
        Output(ids.BACKGROUND_TASK_BADGE, "color"),
        Output(ids.BADGE_TASK_STORE, "data", allow_duplicate=True),
        Input(ids.BADGE_STATUS_INTERVAL, "n_intervals"),
        State(ids.BADGE_TASK_STORE, "data"),
        prevent_initial_call=True,
    )
    def get_task_status(n_intervals: int, task_ids: List) -> str:
        if not task_ids:
            raise PreventUpdate
        for task_id in task_ids:
            task = AsyncResult(task_id, backend=queue.backend, app=queue)
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
    def show_tasks_count(n_intervals: int, task_ids: List) -> str:
        if not task_ids:
            text = f"0 tasks!"
        else:
            n_tasks = len(task_ids)
            text = f"{n_tasks} task" if n_tasks == 1 else f"{n_tasks} tasks"
        return text

    @app.callback(
        Output(ids.BADGE_TASK_STORE, "data", allow_duplicate=True),
        Input(ids.BACKGROUND_TASK_BUTTON, "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def update_badge_color(btn: int):
        if not ctx.triggered_id == ids.BACKGROUND_TASK_BUTTON:
            raise PreventUpdate
        task_ids = Patch()
        color = random.choice(
            ["green", "cyan", "teal", "lime", "yellow", "orange", "blue"]
        )
        task: AsyncResult = set_badge_color.delay((color,))
        task_ids.append(task.id)
        return task_ids

    # NOTE: You can uncomment this callback
    # for disabling submit button when task is submitted
    # @app.callback(
    #     Output(ids.BACKGROUND_TASK_BUTTON, "disabled"),
    #     Input(ids.BADGE_TASK_STORE, "data"),
    # )
    # def disable_task_button(task_ids: List) -> bool:
    #     if task_ids:
    #         return True
    #     return False

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
