import dash

dash.register_page(__name__, path="/")

from automappa.pages.home import layout


def layout():
    return layout.render()
