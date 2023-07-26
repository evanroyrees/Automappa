import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
import string
from typing import Protocol
from dash_extensions.enrich import html, DashProxy, Output, Input

from automappa.components import ids

MAX_CHARS = 24


class SampleNameTextInputDataSource(Protocol):
    def name_is_unique(self, name: str) -> bool:
        ...


def has_symbols_or_whitespace(text: str) -> bool:
    # Define the set of allowed characters (letters, digits, and underscores)
    allowed_chars = string.ascii_letters + string.digits + "_"
    # Check if any character in the string is not in the set of allowed characters
    return any(char not in allowed_chars for char in text)


def exceeds_max_char_length(text: str) -> bool:
    return len(text) >= MAX_CHARS


def render(app: DashProxy, source: SampleNameTextInputDataSource) -> html.Div:
    @app.callback(
        Output(ids.SAMPLE_NAME_TEXT_INPUT, "error"),
        Input(ids.SAMPLE_NAME_TEXT_INPUT, "value"),
        prevent_initial_call=True,
    )
    def update_is_valid_sample_name(input_text: str) -> str:
        if input_text is None:
            raise PreventUpdate
        if not source.name_is_unique(input_text):
            return "Sample name must be unique!"
        if has_symbols_or_whitespace(input_text):
            return "Sample may not contain any symbols or whitespace!"
        if exceeds_max_char_length(input_text):
            return f"Name must be less than {MAX_CHARS}"
        return ""

    @app.callback(
        Output(ids.SAMPLE_NAME_TEXT_INPUT, "value"),
        Input(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_text_input_value_on_submit(submit_btn: int) -> str:
        return ""

    return html.Div(
        dmc.TextInput(
            id=ids.SAMPLE_NAME_TEXT_INPUT,
            label="Sample Name",
            placeholder="i.e. forcepia_sponge",
            description="Provide a name to identify this sample",
            required=True,
        ),
    )
