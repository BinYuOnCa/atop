import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from scipy.signal import savgol_filter
import utilities as utl

import visdcc

from navbar import Navbar
nav = Navbar()


def load_date_list():
    data_list_confirmed, data_list_deaths, data_list_recovered, date_list, region_of_interest = utl.load_data_2()
    return date_list

def load_case_list(region="US"):
    data_list_confirmed, data_list_deaths, data_list_recovered, date_list, region_of_interest = utl.load_data_2()
    return data_list_confirmed[region]

def compute_increase_rate(region='US'):
    data_list_confirmed, date_list = utl.load_data_3(region)
    A = data_list_confirmed
    # print("confirmed data is ", A)
    rate = [(A[k+1] - A[k])/A[k]*100 for k in range(0, len(A)-1)]
    return rate

def load_date_list_2(region='US'):
    data_list_confirmed, date_list = utl.load_data_3(region)
    # print("region is ", region, " date_list is ", date_list)
    return date_list[1:]

def smooth_list(l, window=3, poly=1):
    return savgol_filter(l, window, poly)

body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Covid 19 Status"),
                        html.P(
                            """
                            This coronavirus spreading is changing the world dramatically.
                            """
                        ),
                        dbc.Button("View details", color="secondary"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H2("Confirmed cases"),
                        dcc.Graph(
                            figure={"data": [
                                {"x": load_date_list(), "y": load_case_list("US"), 'mode': "lines+markers", 'name': 'US'},
                                {"x": load_date_list(), "y": load_case_list("Italy"), 'mode': "lines+markers", 'name': 'Italy'},

                            ],
                                "layout": utl.layout
                            }
                        ),
                    ]
                ),
            ]
        ),

        dbc.Row(
            [


                dbc.Col(
                    [
                        html.H2("US daily increase rate"),
                        dcc.Graph(
                            figure={"data": [
                                {"x": load_date_list_2("US"), "y": compute_increase_rate("US"), 'mode': "lines+markers", 'name': 'US'},
                                {"x": load_date_list_2("US"), "y":smooth_list(compute_increase_rate("US"),9,2), 'mode':'lines+markers', 'name':'Smoothed'},

                            ],
                                "layout": utl.layout
                            }
                        ),
                    ]
                ),
            ]
        ),
                        
        dbc.Row(
            [

                dbc.Col(
                    [
                        html.H2("Italy daily increase rate"),
                        dcc.Graph(
                            figure={"data": [
                                {"x": load_date_list_2("Italy"), "y": compute_increase_rate("Italy"), 'mode': "lines+markers", 'name': 'Italy'},
                                {"x": load_date_list_2("Italy"), "y":smooth_list(compute_increase_rate("Italy"),9,2), 'mode':'lines+markers', 'name':'Smoothed'},
                            ],
                                "layout": utl.layout
                            }
                        ),
                    ]
                ),
            ]
        ),
                        
        dbc.Row(
            [

                dbc.Col(
                    [
                        html.H2("China daily increase rate"),
                        dcc.Graph(
                            figure={"data": [
                                {"x": load_date_list_2("China"), "y": compute_increase_rate("China"), 'mode': "lines+markers", 'name': 'China'},
                                {"x": load_date_list_2("China"), "y":smooth_list(compute_increase_rate("China"),9,2), 'mode':'lines+markers', 'name':'Smoothed'},
                            ],
                                "layout": utl.layout
                            }
                        ),
                    ]
                ),
            ]
        ),

    ],
    className="mt-4",
)
                        
footer = html.Script("""
  <script type='text/javascript' src='https://www.counter12.com/ad.js?id=0wd8Zxd0ZW9Ddy4Y'>
  </script>
""")

def Homepage():
    layout = html.Div([
        nav,
        body,
        footer
    ])
    return layout


if __name__ == "__main__":

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
    app.layout = Homepage()
    app.run_server()
