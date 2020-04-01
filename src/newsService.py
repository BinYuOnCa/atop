from newsapi import NewsApiClient
from uszipcode import SearchEngine
from uszipcode import model


import dash_html_components as html

from src.geoService import geoClass 

geo = geoClass()

class NewsAPI:
    def __init__(self, api_key='dc70f60f4aab4cfcaeffba24b1ded39d'):
        self.api_key = api_key
        self.api = NewsApiClient(self.api_key)

    def get_news_from_newsapi(self, counties):    

        news_list = []
        for county in counties: ## for each city, find news that contains the city name or county name or state name
            res_json = self.api.get_everything(qintitle='({} OR {} OR {}) AND coronavirus'.format(county[0],county[1],county[2]), sort_by='publishedAt', \
            language='en')
            if res_json['totalResults'] > 0:
                news_list.append({'res_json':res_json,'county':county})
        if len(news_list)>0:
            all_news = [n['res_json']['articles'] for n in news_list]
            news_list = [item for sublist in all_news for item in sublist]
            news_list = sorted(news_list,key=lambda a:a['publishedAt'],reverse=True)
            return news_list
        else:
            return None


class Gcse:
    def __init__(self,api_key='AIzaSyD6-1mSmVCL-SIuUpKWISPJfh5dmeHWZjc', cse_id='005840374175465383351:57bjmicu65t'):
        self.api_key = api_key
        self.cse_id = cse_id
     
    def google_search(self, search_term, **kwargs):
        api_key = self.api_key
        cse_id = self.cse_id
        cse_service = build("customsearch", "v1", developerKey=api_key)
        res = cse_service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        return res
    
    def news_for_counties(self, counties):
        news_list = []
        for county in counties:
            res_json = self.google_search(search_term='({} {} {}) coronavirus'.format(county[0],county[1],county[2]), sort='date')
            if len(res_json['items']) > 0:
                news_list.append({'res_json':res_json['items'],'county':county})
        if len(news_list)>0:
            all_news = [n['res_json'] for n in news_list]
            news_list = [item for sublist in all_news for item in sublist]
            # news_list = sorted(news_list,key=lambda a:a['publishedAt'],reverse=True)
            news_list = sorted(news_list,key=lambda a:dateparser.parse(a['snippet'].split('...')[0].strip()),reverse=True)
            return news_list
        else:
            return None


class newsClass:

    def test_gcse_news_search(self):     
        gcse_obj = Gcse()
        result = gcse_obj.google_search("fairfax county virginia coronavirus", sort='date')
        return result



    def get_local_news_by_zipcode(self, zipcode = '20171'):    

        counties = geo.get_regions(zipcode, radius= 50)

        if counties is not None:
            try:
                newsAPI = NewsAPI()
                news_list = newsAPI.get_news_from_newsapi(counties)
            except Exception as ex :
                print( ex )
                news_list = None

            if news_list is not None:
                return news_list
            else:  

                gcse_obj = Gcse()

                news_list = gcse_obj.news_for_counties(counties)
                if news_list is not None:
                    return news_list
                else:
                    return None
        else:
            return None



    def show_news_list(self, zipcode="21029"):
        try:
            news_list = self.get_local_news_by_zipcode(zipcode)
        except BaseException:
            news_list = []

        ol = []
        for news in news_list:
            ol.append([news['title'], news['url']])

        try:
            return html.Ol([html.Li(html.A(x[0], href=x[1])) for x in ol])
        except BaseException:
            return html.Ol("API call limit")

# def get_local_news_by_zipcode(zipcode='20171'):

#     search = SearchEngine()
#     zipcode = str(zipcode)
#     zipcode_info = search.by_zipcode(zipcode)  # get info for the given zip code
#     if zipcode_info.zipcode is not None:
#         lat, lng = zipcode_info.lat, zipcode_info.lng
#         radius = 100
#         res = search.query(
#             lat=lat,
#             lng=lng,
#             radius=radius,
#             sort_by=model.SimpleZipcode.population,  # model.Zipcode.median_household_income,
#             ascending=False,
#             returns=20,
#         )  # get 20 biggest cities around 100 miles around the given zip code

#         api = NewsApiClient(api_key='dc70f60f4aab4cfcaeffba24b1ded39d')
#         news_list = []
#         counties = set([(r.post_office_city, r.state, r.county) for r in res])
#         for county in counties:  # for each city, find news that contains the city name or county name or state name
#             res_json = api.get_everything(qintitle='({} OR {} OR {}) AND coronavirus'.format(county[0], county[1], county[2]), sort_by='publishedAt',
#                                           language='en')
#             if res_json['totalResults'] > 0:
#                 news_list.append(res_json)

#         all_news = [n['articles'] for n in news_list]
#         news_list = [item for sublist in all_news for item in sublist]
#         news_list = sorted(news_list, key=lambda a: a['publishedAt'], reverse=True)

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

    #     return news_list
    # else:
    #     return None


if __name__ == '__main__':

    print( show_news_list())