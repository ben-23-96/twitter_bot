import schedule
from twitter.twitter_bot import Twitter_bot
from topics.api_connector import Topics
from messages.message_writer import Message
from birthday.birthday_wisher import Birthday
from os import getcwd
from time import sleep
import traceback


topics = Topics()


def twitter_login():
    twitter_bot = Twitter_bot()
    twitter_bot.login_twitter()
    return twitter_bot


def wish_happy_birthdays():
    message = Message()
    birthday = Birthday()
    birthdays_today = birthday.check_birthdays()
    if birthdays_today:
        for birthday in birthdays_today:
            twitter_bot = twitter_login()
            bday_tweet = message.compose_tweet('birthday', birthday)
            twitter_bot.tweet_text(bday_tweet)


def random_tweet():
    twitter_bot = twitter_login()
    message = Message()

    tweet_topic, tweet_data = topics.random_tweet_topic()

    tweet = message.compose_tweet(tweet_topic, tweet_data)

    if tweet_topic == 'news' or tweet_topic == 'weather':
        twitter_bot.tweet_text(tweet)
    elif tweet_topic == 'nasa':
        twitter_bot.tweet_image(f'{getcwd()}/images/nasa_image.png', tweet)


def reply_to_mentions():
    twitter_bot = twitter_login()
    twitter_bot.reply()


schedule.every().day.at('08:00').do(wish_happy_birthdays)
schedule.every().day.at('09:00').do(random_tweet)
schedule.every().day.at('13:00').do(random_tweet)
schedule.every().day.at('19:00').do(random_tweet)
schedule.every(1).minutes.do(wish_happy_birthdays)
schedule.every(1).hours.do(reply_to_mentions)

while True:
    try:
        schedule.run_pending()
        sleep(30)
    except Exception as error:
        print(f'there has been an error:\n{error}\n\n{traceback.format_exc()}')
        continue
