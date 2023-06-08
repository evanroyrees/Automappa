import dash

dash.register_page(__name__, name="MAG summary")

from automappa.pages.mag_summary import layout


def layout():
    return layout.render()
