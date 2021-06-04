# Data
import pandas as pd
import pickle
# Graphing
import plotly.graph_objects as go
# Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

import utilities as utl

# Navbar
from navbar import Navbar

from plotly.validators.scatter.marker import SymbolValidator
raw_symbols = SymbolValidator().values

def load_data():
    data, data_list_deaths, data_list_recovered, date_list, region_of_interest = utl.load_data()
    return data


# navigation bar
nav = Navbar()

header = html.H3(
    'Choose a zipcode and find nearby status.'
)

search = dcc.Input(
    placeholder='Enter a zipcode...',
    type='text',
    value='21044',
    id='search',
    style=dict(display='flex', justifyContent='center'),

)

output_2 = html.Div(id='output_2',
                    children=[],
                    )

output_22 = html.Div(id='output_22',
                     children=[],
                     )

body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Confirmed cases in tables"),
                        dcc.Graph(
                            figure=utl.organize_figure_structure(load_data())
                        ),
                    ]
                ),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Related news"),
                        html.Ol(utl.show_news_list())

                    ]
                ),
            ]
        ),

    ],

    className="mt-4",
)

def App():
    layout = html.Div([
        nav,
        header,
        search,
        output_2,
        output_22,
        body
    ])
    return layout


def plot_figure(zipcode):

    data, data_list_deaths, data_list_recovered, date_list, region_of_interest = utl.load_data_2()

    #data, date_list = utl.search_by_zipcode(zipcode)

    print(data)

    data = [go.Scatter(x=date_list,
                       y=data,
                       mode="markers+lines",
                       marker_symbol=raw_symbols[0],
                       marker_line_color="red",
                       marker_color="lightskyblue",
                       marker_line_width=2, marker_size=15)]

    graph = dcc.Graph(
        figure={
            'data': data,
            'layout': go.Layout(
                title='{} confirmed case change'.format(zipcode),
                yaxis={'title': 'confirmed case'},
                hovermode='closest'
            )
        }
    )
    return graph
