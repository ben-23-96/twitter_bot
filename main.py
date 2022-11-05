from requests_oauthlib import OAuth1Session
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta
from messages.message_writer import Message
from topics.api_connector import Topics
from birthday.birthday_wisher import Birthday
from spotify.spotify_song import SpotifySongFinder

load_dotenv()

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

    if mentions_data['meta']['result_count'] > 0:
        return mentions_data
    else:
        return False


def reply_to_mentions(mentions):

    for mention in mentions['data']:

        message, reply_id, author_id = mention['text'], mention['id'], mention['author_id']
        user = [user['username'] for user in mentions['includes']
                ['users'] if author_id == user['id']]
        try:
            reply_message = select_reply(message, user[0])

            reply = {"text": reply_message, "reply": {
                "in_reply_to_tweet_id": reply_id}}
            reply_res = oauth.post(url=TWEET_URL, json=reply)
        except:
            continue


def select_reply(message, user):
    tweet_words = message.lower().split()
    print(tweet_words)
    if tweet_words[1] == 'spotify':
        song_finder = SpotifySongFinder()
        date = tweet_words[2]
        song_info = song_finder.get_top_song_info(date)
        reply = message_writer.write_spotify_message(song_info)
        return reply
    elif tweet_words[1] == 'birthday':
        print('bday')
        birthday = Birthday()
        date = tweet_words[2]
        birthday.add_birthday(user, date)
        return 'your birthdays in the diary'
    else:
        return 'howdy'


def wish_happy_birthdays():
    birthday = Birthday()
    birthdays_today = birthday.check_birthdays()
    if birthdays_today:
        for birthday in birthdays_today:
            bday_tweet = message_writer.write_birthday_message(birthday)
            tweet_text(bday_tweet)


def tweet_nasa_image():
    image_data = topic_selector.get_nasa_image()
    title = image_data['title']
    image_obj = image_data['image']
    message = message_writer.write_nasa_message(title)
    tweet_image(image=image_obj, message=message)


def tweet_random_news():
    news_data = topic_selector.get_news()
    message = message_writer.write_news_message(news_data)
    tweet_text(message=message)


def tweet_image(image, message):
    files = {'media': image}
    upload_res = oauth.post(MEDIA_UPLOAD_URL, files=files)
    upload_res_data = upload_res.json()
    media_id = upload_res_data['media_id_string']

    tweet = {"text": message,
             "media": {"media_ids": [media_id]}}
    tweet_res = oauth.post(url=TWEET_URL, json=tweet)


def tweet_text(message):
    tweet = {"text": message}
    tweet_res = oauth.post(url=TWEET_URL, json=tweet)


mentions_in_past_hour = get_mentions_in_past_hour()

if mentions_in_past_hour:
    reply_to_mentions(mentions=mentions_in_past_hour)


current_hour = datetime.utcnow().hour

if current_hour == 8:
    wish_happy_birthdays()

if current_hour == 12:
    tweet_nasa_image()

if current_hour == 9 or current_hour == 15 or current_hour == 18 or current_hour == 21:
    tweet_random_news()
