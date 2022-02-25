from requests import get
from random import choice
from dotenv import load_dotenv
from os import getenv
import urllib.request

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
        self.previous_topics = []

    def random_tweet_topic(self):
        """method that selects a random method of either get_news (with random categories of 'sport', 'general' and 'science),
        get_nasa_image or get_weather providing they have not been used in by the Twitter_bot that day.
        Returns as a string the topic depending on the method called and the data retrieved from the API as a dictionary"""

        if len(self.previous_topics) == 3:
            self.previous_topics = []

        tweet_topics = [(self.get_nasa_image, 'nasa'), (self.get_weather, 'weather'), (self.get_news, 'general'),
                        (self.get_news, 'sport'), (self.get_news, 'science')]
        unused_topics = []

        for topic in tweet_topics:
            if topic not in self.previous_topics:
                unused_topics.append(topic)

        todays_topic = choice(unused_topics)
        self.previous_topics.append(todays_topic)

        tweet_function, tweet_input = todays_topic[0], todays_topic[1]

        tweet_topic, tweet_data = tweet_function(tweet_input)

        return tweet_topic, tweet_data

    def get_news(self, category):
        """takes a string input of either general, sport, science, connects to the newsapi,
        returns a topic of 'news' as a string and a dictionary containing the data of the top article and the news category of it"""

        params = {'apikey': self.news_api_key,
                  'category': category,
                  'language': 'en'}
        response = get(self.news_url, params=params)
        news_data = {'article_data': response.json(
        )['articles'][0], 'news_category': category}
        return 'news', news_data

    def get_weather(self, category):
        """takes a string input of 'weather', connects to the openweather api,
        returns a topic of 'weather' as string and a dictionary containing information on the next 7 days weather"""

        params = {'lat': 53.57,
                  'lon': -2.42,
                  'exclude': 'current,minutely,hourly,alerts',
                  'units': 'metric',
                  'appid': self.weather_api_key}
        response = get(self.weather_url, params=params)
        weather_data = response.json()['daily']
        return 'weather', weather_data

    def get_nasa_image(self, category):
        """takes a string input of 'nasa', connects to the nasa image of the day API,
        saves the images to 'images/nasa_image.png'.
        Returns a topic of 'nasa' as a string and a dictionary containing the title of the image"""

        params = {'api_key': self.nasa_api_key}
        response = get(self.nasa_url, params=params)
        if response.status_code == 200:
            nasa_data = response.json()
            try:
                title = nasa_data['title']
                image = nasa_data['hdurl']
                urllib.request.urlretrieve(image, "images/nasa_image.png")
            except KeyError:
                return 'nasa', {'title': ' '}
            else:
                return 'nasa', {'title': title}
