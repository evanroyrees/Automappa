import dash

dash.register_page(__name__, name="MAG refinement")

from automappa.pages.mag_refinement import layout


def layout():
    return layout.render()
