import logging

from typing import Literal
from dash_extensions.enrich import DashProxy, html
import dash_bootstrap_components as dbc
import dash

from automappa.components import (
    binning_main_upload_store,
    markers_upload_store,
    metagenome_upload_store,
    pages_navbar,
    selected_tables_store,
    samples_store,
    binning_store,
)

from automappa.pages.home.layout import render as render_home_layout
from automappa.pages.mag_refinement.layout import render as render_mag_refinement_layout
from automappa.pages.mag_summary.layout import render as render_mag_summary_layout
from automappa.pages.not_found_404 import render as render_not_found_404


# from automappa.data.source import DataSource

logger = logging.getLogger(__name__)


def render(
    app: DashProxy,
    storage_type: Literal["memory", "session", "local"] = "session",
    clear_data: bool = False,
) -> html.Div:
    # Register blueprints as pages
    # : i.e. home, mag_refinement, mag_summary
    # pages = [
    #     render_home_layout(),
    #     render_mag_refinement_layout(),
    #     render_mag_summary_layout(),
    # ]
    home_page = render_home_layout()
    home_page.register(
        app=app,
        module=home_page.name,
        **{
            "name": home_page.name,
            "description": home_page.description,
            "title": home_page.title,
            "top_nav": True,
            "order": 0,
            "redirects": ["/home"],
            "path": "/",
        }
    )
    mag_refinement_page = render_mag_refinement_layout()
    mag_refinement_page.register(
        app=app,
        module=mag_refinement_page.name,
        **{
            "name": mag_refinement_page.name,
            "description": mag_refinement_page.description,
            "title": mag_refinement_page.title,
            "top_nav": False,
            "order": 1,
        }
    )
    mag_summary_page = render_mag_summary_layout()
    mag_summary_page.register(
        app=app,
        module=mag_summary_page.name,
        **{
            "name": mag_summary_page.name,
            "description": mag_summary_page.description,
            "title": mag_summary_page.title,
            "top_nav": False,
            "order": 2,
        }
    )
    not_found_404_page = render_not_found_404()
    not_found_404_page.register(
        app=app,
        module=not_found_404_page.name,
    )

    # Setup main app layout.
    stores = [
        binning_main_upload_store.render(
            app, storage_type=storage_type, clear_data=clear_data
        ),
        markers_upload_store.render(
            app, storage_type=storage_type, clear_data=clear_data
        ),
        metagenome_upload_store.render(
            app, storage_type=storage_type, clear_data=clear_data
        ),
        samples_store.render(app, storage_type=storage_type, clear_data=clear_data),
        selected_tables_store.render(
            app, storage_type=storage_type, clear_data=clear_data
        ),
        binning_store.render(app),
    ]
    return html.Div(
        children=[
            *stores,
            pages_navbar.render(),
            dash.page_container,
        ],
        style=dict(display="block"),
    )
