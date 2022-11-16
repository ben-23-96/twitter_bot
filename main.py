from requests_oauthlib import OAuth1Session
from os import getenv
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from messages.message_writer import Message
from topics.api_connector import Topics
from birthday.birthday_wisher import Birthday
from spotify.spotify_song import SpotifySongFinder
from logger import EventLogger

load_dotenv()

log = EventLogger()

user_id = getenv('TWITTER_USER_ID')

TWEET_URL = 'https://api.twitter.com/2/tweets'
MEDIA_UPLOAD_URL = 'https://upload.twitter.com/1.1/media/upload.json'
MENTIONS_LOOKUP_URL = f'https://api.twitter.com/2/users/{user_id}/mentions'

topic_selector = Topics()
message_writer = Message()

oauth = OAuth1Session(
    getenv("TWITTER_API_KEY"),
    client_secret=getenv("TWITTER_API_SECRET"),
    resource_owner_key=getenv("TWITTER_API_ACCESS_TOKEN"),
    resource_owner_secret=getenv("TWITTER_API_ACCESS_TOKEN_SECRET"),
)


def get_mentions_in_past_hour():

    dtformat = '%Y-%m-%dT%H:%M:%SZ'
    time = datetime.utcnow()
    one_hour = time - timedelta(hours=1)
    one_hour = one_hour.strftime(dtformat)

    params = {"user.fields": "username",
              "expansions": "author_id", "start_time": one_hour}

    mentions_res = oauth.get(url=MENTIONS_LOOKUP_URL, params=params)

    mentions_data = mentions_res.json()

    if mentions_res.status_code == 200:
        log.add_log_entry('request to retrieve mentions data successful')
    else:
        log.add_log_entry(
            entry=f'error with request to retrieve mentions data, status code of response: {mentions_res.status_code}', is_error=True)
        return None

    if mentions_data['meta']['result_count'] > 0:
        log.add_log_entry(entry='mentions found in the past hour')
        return mentions_data
    else:
        log.add_log_entry(entry='no mentions in past hour')
        return None


def reply_to_mentions(mentions):

    for mention in mentions['data']:

        message, reply_id, author_id = mention['text'], mention['id'], mention['author_id']
        user = [user['username'] for user in mentions['includes']
                ['users'] if author_id == user['id']]

        log.add_log_entry(entry='select_reply function called')
        reply_message = select_reply(message, user[0])

        reply = {"text": reply_message, "reply": {
            "in_reply_to_tweet_id": reply_id}}
        reply_res = oauth.post(url=TWEET_URL, json=reply)

        if reply_res.status_code == 201:
            log.add_log_entry(
                entry=f'succesfully sent reply to user: {user}, message: {reply_message}')
        else:
            log.add_log_entry(
                entry=f'error sending reply, response status code: {reply_res.status_code}, user: {user}, message: {message}', is_error=True)


def select_reply(message, user):

    tweet_words = message.lower().split()
    if tweet_words[1] == 'spotify':
        log.add_log_entry(entry='spotify reply selected')
        try:
            date = tweet_words[2]
        except IndexError:
            log.add_log_entry(
                entry=f'reply not selected the message was: {message}', is_error=True)
            return 'Hello there! Reading is hard for robots I can only read certain things. Read my bio.'

        song_finder = SpotifySongFinder()
        song_info = song_finder.get_top_song_info(date)
        reply = message_writer.write_spotify_message(song_info)
        log.add_log_entry(entry='spotify reply created successfully')
        return reply

    elif tweet_words[1] == 'birthday':
        log.add_log_entry(entry='birthday reply selected')
        birthday = Birthday()

        try:
            date = tweet_words[2]
        except IndexError:
            log.add_log_entry(
                entry=f'reply not selected the message was: {message}', is_error=True)
            return 'Hello there! Reading is hard for robots I can only read certain things. Read my bio.'

        birthday_added = birthday.add_birthday(user, date)
        if birthday_added:
            log.add_log_entry(entry='birthday reply created successfully')
            return 'your birthdays in the diary'
        else:
            return 'your birthday was not added to the diary due to a techincal glitch, please try again'

    else:
        log.add_log_entry(
            entry=f'reply not selected the message was: {message}')
        return 'Hello there! Reading is hard for robots I can only read certain things. Read my bio.'


def tweet_weather_forecast():

    weather_data = topic_selector.get_weather()
    if weather_data:
        message = message_writer.write_weather_message(weather_data)
        log.add_log_entry(entry='tweet_text function called')
        tweet_text(message=message)
    else:
        log.add_log_entry(
            entry='no news returned therefore weather tweet not sent', is_error=True)


def wish_happy_birthdays():

    birthday = Birthday()
    birthdays_today = birthday.check_birthdays()
    if birthdays_today:
        for birthday in birthdays_today:
            bday_tweet = message_writer.write_birthday_message(birthday)
            log.add_log_entry(entry='tweet_text function called')
            tweet_text(bday_tweet)


def tweet_nasa_image():

    image_data = topic_selector.get_nasa_image()
    if image_data:
        title = image_data['title']
        image_obj = image_data['image']
        message = message_writer.write_nasa_message(title)
        log.add_log_entry(entry='tweet_image function called')
        tweet_image(image=image_obj, message=message)
    else:
        log.add_log_entry(
            entry='no image data returned therefore no nasa image tweet sent', is_error=True)


def tweet_random_news():

    news_data = topic_selector.get_news()
    if news_data:
        message = message_writer.write_news_message(news_data)
        log.add_log_entry(entry='tweet_text function called')
        tweet_text(message=message)
    else:
        log.add_log_entry(
            entry='no news data returned therefore random news tweet not sent')


def tweet_image(image, message):

    files = {'media': image}
    upload_res = oauth.post(MEDIA_UPLOAD_URL, files=files)
    try:
        upload_res_data = upload_res.json()
        media_id = upload_res_data['media_id_string']
    except KeyError:
        log.add_log_entry(
            entry=f'error uploading image to twitter media therfore image not tweeted, reponse code of post request: {upload_res.status_code}', is_error=True)
        log.add_log_entry(entry=upload_res.json(), is_error=True)
        return None

    tweet = {"text": message,
             "media": {"media_ids": [media_id]}}
    tweet_res = oauth.post(url=TWEET_URL, json=tweet)

    if tweet_res.status_code == 201:
        log.add_log_entry(entry='image tweeted successfully')
    else:
        log.add_log_entry(
            entry=f'error sending tweet with attached image, response code of post request: {tweet_res.status_code}', is_error=True)
        log.add_log_entry(entry=tweet_res.json(), is_error=True)


def tweet_text(message):

    tweet = {"text": message}
    tweet_res = oauth.post(url=TWEET_URL, json=tweet)

    if tweet_res.status_code == 201:
        log.add_log_entry(entry=f'tweet successful, message: {message}')
    else:
        log.add_log_entry(
            entry=f'error sending tweet, message: {message}, reponse code of post request: {tweet_res.status_code}', is_error=True)
        log.add_log_entry(entry=tweet_res.json())


log.add_log_entry(entry='get_mentions_in_past_hour function called')
mentions_in_past_hour = get_mentions_in_past_hour()

if mentions_in_past_hour:
    log.add_log_entry(entry='reply_to_mentions function called')
    reply_to_mentions(mentions=mentions_in_past_hour)


current_hour = datetime.utcnow().hour
log.add_log_entry(entry=f'the current hour is {current_hour}')

weather_hour = getenv('WEATHER_HOUR')
birthday_hour = getenv('BIRTHDAY_HOUR')
nasa_hour = getenv('NASA_HOUR')

if current_hour == int(weather_hour):
    log.add_log_entry(entry='tweet_weather_forecast function called')
    tweet_weather_forecast()

if current_hour == int(birthday_hour):
    log.add_log_entry(entry='wish_happy_birthdays function called')
    wish_happy_birthdays()

if current_hour == int(nasa_hour):
    log.add_log_entry(entry='tweet_nasa_image function called')
    tweet_nasa_image()

news_hours = json.loads(getenv('NEWS_HOURS'))
if current_hour in news_hours:
    log.add_log_entry(entry='tweet_random_news function called')
    tweet_random_news()

if current_hour == 19:
    try:
        log.delete_old_log_entries()
        log.add_log_entry(
            entry='successfully deleted log entries older than two days')
    except:
        log.add_log_entry(
            entry='error deleting log entries older than two days', is_error=True)
