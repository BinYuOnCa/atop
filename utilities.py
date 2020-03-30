#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 23:26:04 2020

@author: chaowu
"""

import numpy as np
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
from datetime import date
from datetime import timedelta

import plotly.express as px

from flask import jsonify
import pgeocode
import math


df_conf = pd.read_csv('data/time_series_19-covid-Confirmed.csv')
date_cols = [c for c in df_conf.columns if '/20' in c]

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

layout = {
    'plot_bgcolor': colors['background'],
    'paper_bgcolor': colors['background'],
    'font': {'color': colors['text']}
}


def dataSource(category: int) -> str:
    '''
    Return the URL for the given category, which is one of the following:
    Confirmed, Deaths, Recovered

    Return None if the given parameter is none of the above three.

    '''
    base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

    dataSources = {'Confirmed': 'time_series_covid19_confirmed_global.csv',
                   'Deaths': 'time_series_covid19_deaths_global.csv',
                   'Recovered': 'time_series_covid19_recovered_global.csv'}

    fn = dataSources.get(category)

    url_path = base_url+fn if fn else fn
    #print("url path is ", url_path)

    return url_path


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3959  # mile

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d

def row_dist(r, zipinfo):
    dist = distance((zipinfo['latitude'], zipinfo['longitude']), (r['Lat'], r['Long']))
    return dist

def config_geo_layout():

    current_time = str(date.today())

    # print('reading the csv')
    df_conf = pd.read_csv(dataSource('Confirmed'))
    date_cols = [c for c in df_conf.columns if '/20' in c]
    df_conf['total'] = df_conf[date_cols].sum(axis=1)
    df_conf = df_conf[df_conf['total'] > 0]

    df_deaths = pd.read_csv(dataSource('Deaths'))
    df_deaths['total'] = df_deaths[date_cols].sum(axis=1)
    df_deaths = df_deaths[df_deaths['total'] > 0]

    # print('done reading the csv file')

    def get_text(r):
        # print(r['Province/State'])
        if str(r['Province/State']) != 'nan':
            return r['Province/State'] + '<br>' + 'Confirmed: ' + str(r['total'])
        else:
            return r['Country/Region'] + '<br>' + 'Confirmed: ' + str(r['total'])

    df_conf['text'] = df_conf.apply(get_text, axis=1)
    median_val = df_conf['total'].median()

    # scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    #     [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]
    scl = [[0, "rgb(5, 10, 172)"], [0.35, "rgb(40, 60, 190)"], [0.5, "rgb(70, 100, 245)"],
           [0.6, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [1, "rgb(240, 210, 250)"]]

    df_deaths['text'] = df_deaths.apply(get_text, axis=1)

    scl = [[0, "rgb(5, 10, 172)"], [0.35, "rgb(40, 60, 190)"], [0.5, "rgb(70, 100, 245)"],
           [0.6, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [1, "rgb(220, 220, 220)"]]

    median_val_d = df_deaths['total'].median()

    data_d = [dict(
        type='scattergeo',
        # locationmode =  #'USA-states',
        locations="iso_alpha",
        showcountries=True,
        lon=df_deaths['Long'],
        lat=df_deaths['Lat'],
        text=df_deaths['text'],
        mode='markers',
        marker=dict(
            size=8,
            opacity=0.8,
            reversescale=True,
            autocolorscale=False,
            symbol='circle',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale=scl,
            # color_continuous_midpoint = median_val_d,
            cmin=0,
            color=df_deaths['total'],
            cmax=df_deaths['total'].max(),
            colorbar=dict(
                title="CoronaVirus Deaths Total as of 2020/03/13"
            )
        ))]

    layout_d = dict(
        title='CoronaVirus Death Total as of 2020/03/13',
        height=700,
        colorbar=True,
        geo=dict(
            scope='usa',
            projection='natural earth',  # dict( type='albers usa' ),
            showland=True,
            landcolor="rgb(250, 250, 250)",
            subunitcolor="rgb(217, 217, 217)",
            countrycolor="rgb(217, 217, 217)",
            countrywidth=0.5,
            subunitwidth=0.5
        ),
    )

    return data_d, layout_d


def load_data():

    df_Confirmed = pd.read_csv(dataSource("Confirmed"))
    df_Deaths = pd.read_csv(dataSource("Deaths"))
    df_Recovered = pd.read_csv(dataSource("Recovered"))

    #countries = df_Confirmed['Country/Region'].unique()

    date_list = df_Confirmed.columns.to_list()
    date_list = date_list[34:]

    region_of_interest = ['US', 'Germany', 'Italy', 'United Kingdom', 'Canada', 'Iran', 'Spain']

    def update_number_by_region(df=df_Confirmed):
        data_list = []
        for region in region_of_interest:
            #print("region is ", region)
            df_1 = df[df['Country/Region'] == region]
            df_1 = df_1.fillna(0)

            confirmed_number = list(np.sum(np.array(df_1[date_list]), axis=0))
            confirmed_number = [int(x) for x in confirmed_number]
            data_list.append({'x': date_list, 'y': confirmed_number, 'mode': 'lines+markers', 'name': region})

        return data_list

    data_list_confirmed = update_number_by_region(df_Confirmed)
    data_list_deaths = update_number_by_region(df_Deaths)
    data_list_recovered = update_number_by_region(df_Recovered)

    # print(data_list_confirmed)

    return data_list_confirmed, data_list_deaths, data_list_recovered, date_list, region_of_interest

def load_data_2():

    df_Confirmed = pd.read_csv(dataSource("Confirmed"))
    df_Deaths = pd.read_csv(dataSource("Deaths"))
    df_Recovered = pd.read_csv(dataSource("Recovered"))

    #countries = df_Confirmed['Country/Region'].unique()

    date_list = df_Confirmed.columns.to_list()

    region_of_interest = ['US', 'Germany', 'Italy', 'United Kingdom', 'Canada', 'Iran', 'Spain']

    date_list = date_list[35:]

    def update_number_by_region(df=df_Confirmed):
        data_list = {}
        for region in region_of_interest:
            #print("region is ", region)
            df_1 = df[df['Country/Region'] == region]
            df_1 = df_1.fillna(0)

            confirmed_number = list(np.sum(np.array(df_1[date_list]), axis=0))
            confirmed_number = [int(x) for x in confirmed_number]
            data_list[region] = confirmed_number
        return data_list

    data_list_confirmed = update_number_by_region(df_Confirmed)
    data_list_deaths = update_number_by_region(df_Deaths)
    data_list_recovered = update_number_by_region(df_Recovered)

    # print(data_list_confirmed)

    return data_list_confirmed, data_list_deaths, data_list_recovered, date_list, region_of_interest

def load_data_3(region='US'):

    df_Confirmed = pd.read_csv(dataSource("Confirmed"))

    date_list = df_Confirmed.columns.to_list()
    if region == "US":
        limited_date_list = date_list[45:]
    else:
        limited_date_list = date_list[36:]

    def update_number_by_region(df=df_Confirmed):

        df_1 = df[df['Country/Region'] == region]
        df_1 = df_1.fillna(0)

        confirmed_number = list(np.sum(np.array(df_1[limited_date_list]), axis=0))
        confirmed_number = [int(x) for x in confirmed_number]

        return confirmed_number

    data_list_confirmed = update_number_by_region(df_Confirmed)

    # print(data_list_confirmed)

    return data_list_confirmed, limited_date_list

def organize_figure_structure(data):

    figure_data = {
        'data': data,
        'layout': {
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['text']}
        }
    }

    return figure_data


def search_by_zipcode(zipcode="21029"):

    df_conf = pd.read_csv(dataSource("Confirmed"))

    date_cols = [c for c in df_conf.columns if '/20' in c]
    date_cols = date_cols[-1]

    nomi = pgeocode.Nominatim('us')
    zipinfo = nomi.query_postal_code(zipcode)
    dist_vals = df_conf.apply(row_dist, axis=1, zipinfo=zipinfo)
    df_local = df_conf[dist_vals < 100]
    df_local = df_local[date_cols]

    return df_local, date_cols


def fetch_lat_long_by_name():
    from geopy.geocoders import Nominatim
    import pandas as pd

    df_conf = pd.read_csv('../data/time_series_19-covid-Confirmed.csv')
    df_us = df_conf[df_conf['Country/Region'] == 'US']
    location_names = df_us['Province/State'].values.tolist()
    geolocator = Nominatim(user_agent="corona")
    unqueried = location_names
    list_dict = []
    while len(unqueried) > 0:
        for l in location_names:
            try:
                if ',' not in l:
                    location = geolocator.geocode(l + ' State')
                else:
                    location = geolocator.geocode(l)
                unqueried.remove(l)
                list_dict.append({'Province/State': l, 'Lat': location.latitude, 'Long': location.longitude})
            except BaseException:
                print('time out for querying %s' % l)

    latlong_df = pd.DataFrame.from_records(list_dict)
    latlong_df.to_csv('../data/lat_long_by_loc_name.csv')


def get_local_news_by_zipcode(zipcode='20171'):
    from newsapi import NewsApiClient
    from uszipcode import SearchEngine
    from uszipcode import model

    search = SearchEngine()
    zipcode = str(zipcode)
    zipcode_info = search.by_zipcode(zipcode)  # get info for the given zip code
    if zipcode_info.zipcode is not None:
        lat, lng = zipcode_info.lat, zipcode_info.lng
        radius = 100
        res = search.query(
            lat=lat,
            lng=lng,
            radius=radius,
            sort_by=model.SimpleZipcode.population,  # model.Zipcode.median_household_income,
            ascending=False,
            returns=20,
        )  # get 20 biggest cities around 100 miles around the given zip code

        api = NewsApiClient(api_key='dc70f60f4aab4cfcaeffba24b1ded39d')
        news_list = []
        counties = set([(r.post_office_city, r.state, r.county) for r in res])
        for county in counties:  # for each city, find news that contains the city name or county name or state name
            res_json = api.get_everything(qintitle='({} OR {} OR {}) AND coronavirus'.format(county[0], county[1], county[2]), sort_by='publishedAt',
                                          language='en')
            if res_json['totalResults'] > 0:
                news_list.append(res_json)

        all_news = [n['articles'] for n in news_list]
        news_list = [item for sublist in all_news for item in sublist]
        news_list = sorted(news_list, key=lambda a: a['publishedAt'], reverse=True)

        # just get the titles:
        #news_list = [news['title'] for news in news_list]
        #news_list = list(set(news_list))
        # In [104]: news_list[0]
        # Out[104]:
        # {'source': {'id': None, 'name': 'Arlnow.com'},
        #  'author': 'ARLnow.com',
        #  'title': 'Another Jump in Coronavirus Cases in Arlington, Fairfax County',
        #  'description': 'Arlington and Fairfax counties are continuing to report an expected -- but concerning -- upward trajectory in COVID-19 cases as testing continues to ramp up.\r\n\r\nAs of noon on Wednesday, Arlington had 46 known coronavirus cases, an increase from 36 cases on Tu…',
        #  'url': 'https://www.arlnow.com/2020/03/25/another-jump-in-coronavirus-cases-in-arlington-fairfax-county/',
        #  'urlToImage': 'https://s26551.pcdn.co/wp-content/uploads/2020/03/Screen-Shot-2020-03-25-at-12.34.32-PM.jpg',
        #  'publishedAt': '2020-03-25T17:10:14Z',
        #  'content': 'Arlington and Fairfax counties are continuing to report an expected — but concerning — upward trajectory in COVID-19 cases as testing continues to ramp up.\r\nAs of noon on Wednesday, Arlington had 46 known coronavirus cases, an increase from 36 cases on Tuesda… [+2164 chars]'}
        #print("searched result: ", zipcode, news_list)

        return news_list
    else:
        return None


def show_news_list(zipcode="21029"):
    try:
        news_list = get_local_news_by_zipcode(zipcode)
    except BaseException:
        news_list = []

    ol = []
    for news in news_list:
        ol.append([news['title'], news['url']])
    try:
        return html.Ol([html.Li(html.A(x[0], href=x[1])) for x in ol])
    except BaseException:
        return html.Ol("API call limit")


if __name__ == "__main__":

    df_local, date_cols = search_by_zipcode()

    print(df_local)

    #news_list = get_local_news_by_zipcode()
    # print(news_list)
