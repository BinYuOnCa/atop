import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import utilities as utl

from navbar import Navbar
nav = Navbar()

body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Under construction"),
                    ],
                    md=4,
                ),
            ]
        ),

    ],
    className="mt-4",
)

def load_layout():
    layout = html.Div([
        nav,
        body
    ])
    return layout


if __name__ == "__main__":

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
    app.layout = load_layout()
    app.run_server()
