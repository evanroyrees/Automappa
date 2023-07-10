from typing import Protocol
from dash_extensions.enrich import (
    DashProxy,
    Input,
    Output,
    html,
    State,
    ctx,
)
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from automappa.components import ids
from automappa.pages.home.components import (
    binning_upload,
    cytoscape_connections_upload,
    markers_upload,
    metagenome_upload,
    sample_name_text_input,
)

# LOGIC:
# Steps:
# 1. Upload metagenome
# 2. Upload binning (will eventually link to metagenome)
# 3. Upload markers (will eventually link to binning contigs)
# 4. Upload cytoscape connections (optional will eventually link to metagenome)
# 5. Finish upload (unique sample name required as text input to act as link b/w uploaded data)
# On completion (adds metagenome card to home page)


class UploadStepperDataSource(Protocol):
    def name_is_unique(self, name: str) -> bool:
        ...


def render(app: DashProxy, source: UploadStepperDataSource) -> html.Div:
    @app.callback(
        Output(ids.UPLOAD_STEPPER, "active", allow_duplicate=True),
        Input(ids.UPLOAD_STEPPER_BACK_BUTTON, "n_clicks"),
        Input(ids.UPLOAD_STEPPER_NEXT_BUTTON, "n_clicks"),
        State(ids.UPLOAD_STEPPER, "active"),
        prevent_initial_call=True,
    )
    def update_active_step(back_btn: int, next_btn: int, current_step: int) -> int:
        button_id = ctx.triggered_id
        step = current_step if current_step is not None else ACTIVE
        if button_id == ids.UPLOAD_STEPPER_BACK_BUTTON:
            step = step - 1 if step > MIN_STEP else step
        else:
            step = step + 1 if step < MAX_STEP else step
        return step

    @app.callback(
        Output(ids.UPLOAD_STEPPER_BACK_BUTTON, "disabled"),
        Input(ids.UPLOAD_STEPPER, "active"),
        prevent_initial_call=True,
    )
    def disable_back_button_on_upload_metagenome_step(
        current_step: int,
    ) -> bool:
        is_disabled = True
        if current_step == MIN_STEP:
            return is_disabled
        return not is_disabled

    @app.callback(
        Output(ids.UPLOAD_STEPPER_NEXT_BUTTON, "disabled", allow_duplicate=True),
        Input(ids.METAGENOME_UPLOAD, "isCompleted"),
        Input(ids.UPLOAD_STEPPER, "active"),
        prevent_initial_call=True,
    )
    def toggle_next_button_on_metagenome_upload(
        is_completed: bool,
        current_step: int,
    ) -> bool:
        if current_step != METAGENOME_UPLOAD_STEP:
            raise PreventUpdate
        return not is_completed

    @app.callback(
        Output(ids.UPLOAD_STEPPER_NEXT_BUTTON, "disabled", allow_duplicate=True),
        Input(ids.BINNING_UPLOAD, "isCompleted"),
        Input(ids.UPLOAD_STEPPER, "active"),
        prevent_initial_call=True,
    )
    def toggle_next_button_on_binning_upload(
        is_completed: bool, current_step: int
    ) -> bool:
        if current_step != BINNING_UPLOAD_STEP:
            raise PreventUpdate
        return not is_completed

    @app.callback(
        Output(ids.UPLOAD_STEPPER_NEXT_BUTTON, "disabled", allow_duplicate=True),
        Input(ids.MARKERS_UPLOAD, "isCompleted"),
        Input(ids.UPLOAD_STEPPER, "active"),
        prevent_initial_call=True,
    )
    def toggle_next_button_on_marker_upload(
        is_completed: bool, current_step: int
    ) -> bool:
        if current_step != MARKERS_UPLOAD_STEP:
            raise PreventUpdate
        return not is_completed

    @app.callback(
        Output(ids.UPLOAD_STEPPER_NEXT_BUTTON, "disabled", allow_duplicate=True),
        Input(ids.SAMPLE_NAME_TEXT_INPUT, "error"),
        Input(ids.SAMPLE_NAME_TEXT_INPUT, "value"),
        Input(ids.UPLOAD_STEPPER, "active"),
        prevent_initial_call=True,
    )
    def toggle_next_button_on_sample_name_input(
        text_input_error: str, text_input_value: str, current_step: int
    ) -> bool:
        if current_step != SAMPLE_NAME_STEP:
            raise PreventUpdate
        return not text_input_value or text_input_error != ""

    @app.callback(
        Output(ids.UPLOAD_STEPPER_NEXT_BUTTON, "disabled", allow_duplicate=True),
        Input(ids.UPLOAD_STEPPER, "active"),
        prevent_initial_call=True,
    )
    def disable_next_button_on_completed_step(current_step: int) -> bool:
        if current_step != MAX_STEP:
            raise PreventUpdate
        return True

    @app.callback(
        Output(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "disabled"),
        Input(ids.SAMPLE_NAME_TEXT_INPUT, "value"),
    )
    def toggle_submit_button(text_input: str) -> bool:
        return not text_input

    @app.callback(
        Output(ids.UPLOAD_STEPPER, "active", allow_duplicate=True),
        Input(ids.UPLOAD_STEPPER_SUBMIT_BUTTON, "n_clicks"),
        prevent_initial_call=True,
    )
    def on_submit_button(submit_btn: int) -> int:
        return ACTIVE

    @app.callback(
        Output(ids.UPLOAD_STEPPER, "active", allow_duplicate=True),
        Input(ids.CLOSE_MODAL_BUTTON, "n_clicks"),
        prevent_initial_call=True,
    )
    def on_close_modal_button(close_modal_btn: int) -> int:
        return ACTIVE

    def get_icon(icon: str, height: int = 20) -> DashIconify:
        return DashIconify(icon=icon, height=height)

    MIN_STEP = 0
    METAGENOME_UPLOAD_STEP = 0
    BINNING_UPLOAD_STEP = 1
    MARKERS_UPLOAD_STEP = 2
    CONNECTIONS_UPLOAD_STEP = 3
    SAMPLE_NAME_STEP = 4
    MAX_STEP = 5
    ACTIVE = 0

    upload_metagenome_step = dmc.StepperStep(
        label="First step",
        description="Upload metagenome",
        icon=get_icon("tabler:dna-2-off"),
        iconSize=30,
        progressIcon=get_icon("tabler:dna-2-off"),
        completedIcon=get_icon("tabler:dna-2"),
        children=[
            dmc.Text(
                "Upload your sample's metagenome assembly fasta file",
                align="center",
            ),
            metagenome_upload.render(app),
        ],
    )
    upload_binning_step = dmc.StepperStep(
        label="Second step",
        description="Upload binning",
        icon=get_icon("ph:chart-scatter"),
        iconSize=30,
        progressIcon=get_icon("ph:chart-scatter"),
        completedIcon=get_icon("ph:chart-scatter-bold"),
        children=[
            dmc.Group(
                children=[
                    dmc.Text(
                        "Upload the corresponding main binning results",
                        align="center",
                    ),
                    dmc.Anchor(
                        dmc.Tooltip(
                            get_icon(
                                "material-symbols:info-outline",
                                height=15,
                            ),
                            label=dmc.Code(
                                "autometa-binning --output-main <this-output-file>"
                            ),
                            color="gray",
                            withArrow=True,
                            position="right",
                            radius="md",
                        ),
                        href="https://autometa.readthedocs.io/en/latest/step-by-step-tutorial.html#binning",
                        target="_blank",
                        underline=False,
                        color="dark",
                    ),
                ],
                spacing="xs",
            ),
            binning_upload.render(app),
        ],
    )

    upload_markers_step = dmc.StepperStep(
        label="Third step",
        description="Upload markers",
        icon=get_icon("fluent:document-dismiss-24-regular"),
        iconSize=30,
        progressIcon=get_icon("fluent:document-dismiss-24-regular"),
        completedIcon=get_icon("fluent:document-checkmark-24-regular"),
        children=[
            dmc.Group(
                children=[
                    dmc.Text(
                        "Upload the corresponding marker annotation results",
                        align="center",
                    ),
                    dmc.Anchor(
                        dmc.Tooltip(
                            get_icon(
                                "material-symbols:info-outline",
                                height=15,
                            ),
                            label=dmc.Code(
                                "autometa-markers --out <markers-output-file>"
                            ),
                            color="gray",
                            withArrow=True,
                            position="right",
                            radius="md",
                        ),
                        href="https://autometa.readthedocs.io/en/latest/step-by-step-tutorial.html#single-copy-markers",
                        target="_blank",
                        color="dark",
                        underline=False,
                    ),
                ],
            ),
            markers_upload.render(app),
        ],
    )

    connections_upload_step = dmc.StepperStep(
        label="Fourth step",
        description="Upload connections",
        icon=get_icon("bx:network-chart"),
        iconSize=30,
        progressIcon=get_icon("bx:network-chart"),
        completedIcon=get_icon("bx:network-chart"),
        children=[
            dmc.Group(
                children=[
                    dmc.Text("Upload corresponding cytoscape connections"),
                    dmc.Text("(optional)", weight=500, color="orange"),
                    dmc.Anchor(
                        dmc.Tooltip(
                            get_icon(
                                "material-symbols:info-outline",
                                height=15,
                            ),
                            label="Mads Albertsen tutorial on generating paired-end connections",
                            color="gray",
                            withArrow=True,
                            position="right",
                            radius="md",
                        ),
                        href="https://madsalbertsen.github.io/multi-metagenome/docs/step10.html",
                        target="_blank",
                        underline=False,
                        color="dark",
                    ),
                    dmc.Anchor(
                        dmc.Tooltip(
                            get_icon("openmoji:github", height=15),
                            label="https://github.com/MadsAlbertsen/multi-metagenome",
                            color="gray",
                            withArrow=True,
                            position="right",
                            radius="md",
                        ),
                        href="https://github.com/MadsAlbertsen/multi-metagenome",
                        target="_blank",
                        underline=False,
                        color="dark",
                    ),
                ],
                spacing="xs",
            ),
            cytoscape_connections_upload.render(app),
        ],
    )

    name_sample_step = dmc.StepperStep(
        label="Fifth step",
        description="Name Sample",
        icon=get_icon("mdi:rename-outline"),
        iconSize=30,
        progressIcon=get_icon("mdi:rename-outline"),
        completedIcon=get_icon("mdi:rename"),
        children=[
            dmc.Text(
                "Supply a unique sample name to group your metagenome annotations"
            ),
            sample_name_text_input.render(app, source),
        ],
    )

    completed_step = dmc.StepperCompleted(
        children=[
            dmc.Text(
                "That's it! Click the back button to go to a previous step or submit to save this dataset",
                align="center",
            ),
            dmc.Center(
                dmc.Button(
                    "Submit",
                    id=ids.UPLOAD_STEPPER_SUBMIT_BUTTON,
                    leftIcon=[get_icon("line-md:upload-outline")],
                    variant="gradient",
                    gradient={"from": "#CA2270", "to": "#F36E2D"},
                )
            ),
        ]
    )

    return html.Div(
        dmc.Container(
            [
                dmc.Stepper(
                    id=ids.UPLOAD_STEPPER,
                    active=ACTIVE,
                    breakpoint="md",
                    color="dark",
                    children=[
                        upload_metagenome_step,
                        upload_binning_step,
                        upload_markers_step,
                        connections_upload_step,
                        name_sample_step,
                        completed_step,
                    ],
                ),
                dmc.Group(
                    position="center",
                    mt="xl",
                    children=[
                        dmc.Button(
                            "Back",
                            id=ids.UPLOAD_STEPPER_BACK_BUTTON,
                            variant="outline",
                            color="dark",
                            disabled=True,
                        ),
                        dmc.Button(
                            "Next step",
                            id=ids.UPLOAD_STEPPER_NEXT_BUTTON,
                            disabled=True,
                            variant="outline",
                            color="dark",
                        ),
                    ],
                ),
            ]
        )
    )
