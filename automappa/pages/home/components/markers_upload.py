from dash_extensions.enrich import DashProxy
import dash_uploader as du
from automappa.components import ids


def render(app: DashProxy) -> du.Upload:
    return du.Upload(
        id=ids.MARKERS_UPLOAD,
        text="Drag and Drop or Select marker annotations file",
        default_style={
            "width": "100%",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "margin": "10px",
        },
        max_files=1,
        # 10240 MB = 10GB
        max_file_size=10240,
    )