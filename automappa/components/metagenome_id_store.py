from typing import Dict, List, Literal
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (
    dcc,
    DashProxy,
    State,
    Input,
    Serverside,
    Output,
    ALL,
)
from automappa.components import ids
from automappa.data.database import redis_backend


def render(
    app: DashProxy,
    storage_type: Literal["memory", "session", "local"] = "session",
    clear_data: bool = False,
) -> dcc.Store:
    @app.callback(
        Output(ids.METAGENOME_ID_STORE, "data"),
        Input(
            {"type": ids.SAMPLE_CARD_TYPE, ids.SAMPLE_CARD_INDEX: ALL},
            "withBorder",
        ),
        State({"type": ids.SAMPLE_CARD_TYPE, ids.SAMPLE_CARD_INDEX: ALL}, "id"),
        prevent_initial_call=True,
    )
    def update_metagenome_id(
        sample_cards_borders: List[str], sample_cards_ids: List[Dict[str, str]]
    ) -> int:
        if not any(sample_cards_borders):
            raise PreventUpdate
        sample_card_index = [
            i for i, border in enumerate(sample_cards_borders) if border
        ][0]
        metagenome_id = sample_cards_ids[sample_card_index].get(ids.SAMPLE_CARD_INDEX)
        return Serverside(metagenome_id, backend=redis_backend)

    return dcc.Store(
        id=ids.METAGENOME_ID_STORE,
        storage_type=storage_type,
        clear_data=clear_data,
    )
