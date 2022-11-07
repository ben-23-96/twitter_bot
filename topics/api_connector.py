from requests import get
from random import choice
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Topics:
    def __init__(self):
        """class that retrieves to a news API, weather API and nasa daily image API
        to be used as stories and topics to tweet about"""

        self.news_api_key = getenv('NEWS_API_KEY')
        self.weather_api_key = getenv('WEATHER_API_KEY')
        self.nasa_api_key = getenv('NASA_API_KEY')
        self.news_url = 'https://newsapi.org/v2/top-headlines?'
        self.weather_url = 'https://api.openweathermap.org/data/2.5/onecall?'
        self.nasa_url = 'https://api.nasa.gov/planetary/apod?'

    def get_news(self):
        """connects to the newsapi using a random news category, returns a dictionary containing the data of the top article and the news category of it"""

        categories = ['business', 'entertainment',
                      'health', 'science', 'sports', 'technology']
        category = choice(categories)
        params = {'apikey': self.news_api_key,
                  'category': category,
                  'language': 'en'}
        response = get(self.news_url, params=params)
        try:
            article_data = response.json()['articles'][0]
        except KeyError:
            print('error getting news data')
            print(response.status_code, response.json())
            return False
        news_data = {'article_data': article_data, 'news_category': category}
        return news_data

    def get_weather(self):
        """connects to the openweather api, returns a dictionary containing information on the next 7 days weather"""

        params = {'lat': 53.57,
                  'lon': -2.42,
                  'exclude': 'current,minutely,hourly,alerts',
                  'units': 'metric',
                  'appid': self.weather_api_key}
        response = get(self.weather_url, params=params)
        weather_data = response.json()['daily']
        return weather_data

    def get_nasa_image(self):
        """connects to the nasa image of the day API, returns dictionary containing the title of the image and the image"""

        params = {'api_key': self.nasa_api_key}
        response = get(self.nasa_url, params=params)
        print(response.status_code)
        if response.status_code == 200:
            nasa_data = response.json()
            try:
                title = nasa_data['title']
                image_url = nasa_data['hdurl']
            except KeyError:
                print('key error')
                return False
            response = get(image_url, stream=True)
            image_object = response.content
            image_data = {'title': title, 'image': image_object}
            return image_data
        else:
            print(response.json())
