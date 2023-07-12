#!/usr/bin/env python

from typing import List, Protocol
from dash_extensions.enrich import DashProxy, Output, Input, html, ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from automappa.components import ids


class RefinementsClearButtonDataSource(Protocol):
    def clear_refinements(self, metagenome_id: int) -> int:
        ...

    def has_user_refinements(self, metagenome_id: int) -> bool:
        ...


def render(app: DashProxy, source: RefinementsClearButtonDataSource) -> html.Div:
    @app.callback(
        Output(ids.REFINEMENTS_CLEARED_NOTIFICATION, "children"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.REFINEMENTS_CLEAR_BUTTON, "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_refinements_callback(metagenome_id: int, btn: int) -> dmc.Notification:
        deleted_refinements_count = source.clear_refinements(metagenome_id)
        message = f"Successfully cleared {deleted_refinements_count:,}"
        title = (
            "Refinement cleared!"
            if deleted_refinements_count == 1
            else "Refinements cleared!"
        )
        message += " refinement" if deleted_refinements_count == 1 else " refinements"
        return dmc.Notification(
            id="simple-notify",
            action="show",
            message=message,
            title=title,
            icon=DashIconify(icon="icomoon-free:fire", color="#f78f1f"),
            color="dark",
            autoClose=60000,
        )

    @app.callback(
        Output(ids.REFINEMENTS_CLEAR_BUTTON, "disabled"),
        Input(ids.METAGENOME_ID_STORE, "data"),
        Input(ids.REFINEMENTS_CLEARED_NOTIFICATION, "children"),
        Input(ids.MAG_REFINEMENTS_SAVE_BUTTON, "n_clicks"),
    )
    def disable_clear_button(
        metagenome_id: int, cleared_notification: List[dmc.Notification], save_btn: int
    ) -> bool:
        return not source.has_user_refinements(metagenome_id)

    return html.Div(
        [
            dmc.Button(
                children=[dmc.Text("Clear Refinements")],
                id=ids.REFINEMENTS_CLEAR_BUTTON,
                variant="filled",
                color="red",
                leftIcon=DashIconify(icon="icomoon-free:fire", color="white"),
            ),
            html.Div(id=ids.REFINEMENTS_CLEARED_NOTIFICATION),
        ]
    )
