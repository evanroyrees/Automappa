from typing import Literal
from dash_extensions.enrich import dcc, DashProxy
from automappa.components import ids


def render(
    app: DashProxy,
    storage_type: Literal["memory", "session", "local"] = "session",
    clear_data: bool = False,
) -> dcc.Store:
    return dcc.Store(
        id=ids.TASK_ID_STORE,
        storage_type=storage_type,
        clear_data=clear_data,
    )
