from dash_extensions.enrich import DashProxy
import dash_uploader as du
from automappa.components import ids


def render(app: DashProxy) -> du.Upload:
    return du.Upload(
        id=ids.BINNING_UPLOAD,
        text="Drag and Drop or Select binning-main file",
        default_style={
            "width": "100%",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "margin": "10px",
        },
        max_files=1,
        max_file_size=10240,
    )
