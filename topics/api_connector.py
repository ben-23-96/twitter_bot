from requests import get
from random import choice
from dotenv import load_dotenv
from os import getenv
from logger import EventLogger

load_dotenv()

log = EventLogger()


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
        log.add_log_entry(entry='getting news data from news api')

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
            log.add_log_entry(
                entry=f'error getting news data status code of request: {response.status_code}', is_error=True)
            log.add_log_entry(entry=response.json(), is_error=True)
            return None

        log.add_log_entry(entry='news data returned from api')
        news_data = {'article_data': article_data, 'news_category': category}
        return news_data

    def get_weather(self):
        """connects to the openweather api, returns a dictionary containing information on the next 7 days weather"""
        log.add_log_entry(entry='getting weather data from weather api')

        params = {'lat': 53.57,
                  'lon': -2.42,
                  'exclude': 'current,minutely,hourly,alerts',
                  'units': 'metric',
                  'appid': self.weather_api_key}
        response = get(self.weather_url, params=params)

        try:
            weather_data = response.json()['daily']
        except KeyError:
            log.add_log_entry(
                entry=f'error getting weather data status code of request: {response.status_code}', is_error=True)
            log.add_log_entry(entry=response.json(), is_error=True)
            return None

        log.add_log_entry(entry='weather data returned from api')
        return weather_data

    def get_nasa_image(self):
        """connects to the nasa image of the day API, returns dictionary containing the title of the image and the image"""
        log.add_log_entry(entry='getting nasa image from nasa api')

        params = {'api_key': self.nasa_api_key}
        response = get(self.nasa_url, params=params)
        if response.status_code == 200:
            log.add_log_entry(
                entry='nasa api returned response with 200 status code')
            nasa_data = response.json()
            try:
                title = nasa_data['title']
                # get the image url from the nasa api
                image_url = nasa_data['hdurl']
            except KeyError:
                log.add_log_entry(
                    entry='key error nasa api response did not contain a hdurl, possible different format today', is_error=True)
                return None
            try:
                response = get(image_url, stream=True)  # stream the image
                image_object = response.content
                image_data = {'title': title, 'image': image_object}
            except:
                log.add_log_entry(
                    entry=f'error streaming image from hdurl: {image_url}, status code: {response.status_code}', is_error=True)
                return None

            log.add_log_entry(
                entry='nasa image successfully streamed using url retrieved from api')
            return image_data
        else:
            log.add_log_entry(
                entry=f'error getting data from nasa api code of request: {response.status_code}', is_error=True)
            log.add_log_entry(entry=response.json(), is_error=True)
            return None
