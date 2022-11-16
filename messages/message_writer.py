from datetime import datetime, timedelta
from random import choice


class Message:
    def __init__(self):
        """class that takes the data returned from Birthday, Spotify, and Topics classes
        and uses it to compose messages that can be tweeted"""
        pass

    def write_news_message(self, data):
        """input is dictionary from the Topics class's get_news method, writes a message to be tweeted'"""

        news_article = data['article_data']
        news_topic = data['news_category']
        article_string = f"\n{news_article['title']}\n{news_article['url']}"

        message_options = [f"some fascinating {news_topic} news:{article_string}",
                           f"wow look at this {news_topic} news:{article_string}",
                           f"interesting developments in the {news_topic} world, read about it here: {article_string}",
                           f"never a dull moment in {news_topic}. {article_string}",
                           f"{news_topic} news that has peaked my interest: {article_string}",
                           f"can't believe this {news_topic} news. {article_string}",
                           f"seen this {news_topic} news coming a mile off. {article_string}",
                           f"been waiting a long time for {news_topic} news like this. {article_string}",
                           f"{news_topic}! {news_topic}! read all about it!! {article_string}"]

        message = choice(message_options)
        return message

    def write_weather_message(self, data):
        """input is a dictionary from the Topic class's get_weather method, writes a message to be tweeted"""

        message = 'The next 7 days weather:\n'
        day = datetime.now()
        for weather in data:
            day_name = day.strftime('%A')
            type = weather['weather'][0]['main']
            temp = weather['temp']['day']
            id = weather['weather'][0]['id']
            message = message + f"{day_name} {type} {temp}C\n"
            day = day + timedelta(days=1)

        return message

    def write_nasa_message(self, data):
        """input is a dictionary from the Topic class's get_nasa_image method, writes a message to be tweeted"""

        title = data
        message = f"cool image from nasa\n{title}"
        return message

    def write_spotify_message(self, data):
        """input is a dictionary from the Spotify class's get_top_song_info method, writes a message to be tweeted"""
        if data['song_found']:
            link = data['link']
            song = data['song']
            artist = data['artist']
            date = data['date']
            message = f'The number one song on {date} was {song} by {artist}, listen here:\n{link}'
            return message
        else:
            message = f'Could not find the song on Billoards website for the date: {date}. Try another date or check format is correct YYYY-MM-DD.'
            return message

    def write_birthday_message(self, data):
        """input is list item containing a dictionary from the Birthday class's check_birthdays method, writes a message to be tweeted"""

        user = data['user']
        age = data['age']
        message = f"{user} Happy Birthday, you are {age} today, well done."
        return message
