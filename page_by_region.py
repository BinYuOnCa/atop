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
# Navbar
from navbar import Navbar

import utilities as utl

from plotly.validators.scatter.marker import SymbolValidator
raw_symbols = SymbolValidator().values


nav = Navbar()

header = html.H3(
    'Select a region/country name!'
)

def load_options():
    data_list_confirmed, data_list_deaths, data_list_recovered, date_list, region_of_interest = utl.load_data_2()
    options = [{'label': x, 'value': x} for x in region_of_interest]

    return options


options = load_options()

dropdown = html.Div(dcc.Dropdown(
    id='pop_dropdown',
    options=options,
    value='US'
))

output_1 = html.Div(id='output_1',
                    children=[],
                    )

def App():
    layout = html.Div([
        nav,
        header,
        dropdown,
        output_1
    ])
    return layout

def plot_figure(region):

    data_list_confirmed, data_list_deaths, data_list_recovered, date_list, region_of_interest = utl.load_data_2()

    #print(region, data_list_confirmed[region])
    #print("date list ", date_list)

    data = [go.Scatter(x=date_list,
                       y=data_list_confirmed[region],
                       mode="markers+lines",
                       marker_symbol=raw_symbols[4],
                       marker_line_color="blue",
                       marker_color="red",
                       marker_line_width=2, marker_size=15)]

    graph = dcc.Graph(
        figure={
            'data': data,
            'layout': go.Layout(
                title='{} confirmed case change over date'.format(region),
                yaxis={'title': 'Population'},
                hovermode='closest'
            )
        }
    )
    return graph
