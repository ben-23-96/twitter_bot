from datetime import datetime, timedelta
import logging
from os import environ
import re
from requests_oauthlib import OAuth1Session
from dateutil.parser import parse as dateparser
import boto3
import json
import pprint

####                                                                                           ####
#### NUKED BY ELON, APIPOCALYPSE, CAN NO LONGER READ TWEETS ON FREE TIER -> REPLIES IN THE BIN #### 
####                                                                                           ####

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

user_id = environ.get('TWITTER_USER_ID')
print(user_id)
print(environ.get("TWITTER_API_KEY"),environ.get("TWITTER_API_SECRET"),environ.get("TWITTER_API_ACCESS_TOKEN"),environ.get("TWITTER_API_ACCESS_TOKEN_SECRET"))

MENTIONS_LOOKUP_URL = f'https://api.twitter.com/2/users/{user_id}/mentions'
TWEET_URL = 'https://api.twitter.com/2/tweets'

oauth = OAuth1Session(
            environ.get("TWITTER_API_KEY"),
            client_secret=environ.get("TWITTER_API_SECRET"),
            resource_owner_key=environ.get("TWITTER_API_ACCESS_TOKEN"),
            resource_owner_secret=environ.get(
                "TWITTER_API_ACCESS_TOKEN_SECRET"),
        )


def lambda_handler(event, context):
    try:
        mentions_in_past_hour = get_mentions_in_past_hour()
    
        if mentions_in_past_hour:
            logger.info('reply_to_mentions function called')
            reply_to_mentions(mentions=mentions_in_past_hour)
            message = "replies sent succesfully"
        else:
            message = "no replies to send"
        return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': message,
                }),
            }
    except Exception as e:
        logger.exception(
            'An error occurred, traceback message:\n {}'.format(e))

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }


def get_mentions_in_past_hour():

    dtformat = '%Y-%m-%dT%H:%M:%SZ'
    time = datetime.utcnow()
    one_hour = time - timedelta(hours=1)
    one_hour = one_hour.strftime(dtformat)

    params = {"user.fields": "username",
              "expansions": "author_id", "start_time": one_hour}

    # retrieve data for the mentions recieved in the past hour from the twitter api
    mentions_res = oauth.get(url=MENTIONS_LOOKUP_URL, params=params)
    print(mentions_res.text)

    mentions_data = mentions_res.json()
    pprint.pprint(mentions_data, indent=2)

    if mentions_res.status_code == 200:
        logger.info('request to retrieve mentions data successful')
    else:
        logger.error(
            f'error with request to retrieve mentions data, status code of response: {mentions_res.status_code}, response {mentions_res.text}')
        return None

    # if there are mentions from the past hour
    if mentions_data['meta']['result_count'] > 0:
        logger.info('mentions found in the past hour')
        return mentions_data
    else:
        logger.info('no mentions in past hour')
        return None


def reply_to_mentions(mentions):

    for mention in mentions['data']:  # loop for each tweet mention recieved

        message, reply_id, author_id = mention['text'], mention['id'], mention['author_id']
        user = [user['username'] for user in mentions['includes']
                ['users'] if author_id == user['id']]  # username of user who mentioned the bot account

        logger.info('select_reply function called')
        reply_message = select_reply(message, user[0])  # create reply messsage

        reply = {"text": reply_message, "reply": {
            "in_reply_to_tweet_id": reply_id}}
        # send reply tweet using twitter api
        reply_res = oauth.post(url=TWEET_URL, json=reply)

        if reply_res.status_code == 201:
            logger.info(
                f'succesfully sent reply to user: {user}, message: {reply_message}')
        else:
            logger.error(
                f'error sending reply, response status code: {reply_res.status_code}, user: {user}, message: {message}')


def select_reply(message, user):
    # messages to be recieved in form @botaccount spotify/birthday YYYY-MM-DD and strings handled accordingly
    lowercase_message = message.lower()
    if 'spotify' in lowercase_message:
        logger.info('spotify reply selected')
        try:
            date_match = re.search(
                r'\b((\d{4}[-/]\d{2}[-/]\d{2})|(\d{2}[-/]\d{2}[-/]\d{4}))\b', message)
            date = dateparser(date_match.group(), fuzzy=True)
            date_str = date.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(
                f'reply not selected the message was: {message}, error:{e}')
            return 'Hello there! It seems you have may have been trying to use my spotify song finding feature, however your date is invalid.'
        try:
            lambda_client = boto3.client('lambda')
            # invoke the spotify song lambda function to find the top song on the given year
            response = lambda_client.invoke(
                FunctionName='twiter_bot_spotify_song',
                InvocationType='RequestResponse',
                Payload=json.dumps({'date': date_str})
            )
            response_payload = json.loads(response['Payload'].read())
            if 'FunctionError' in response or response_payload.get('statusCode') != 200:
                logger.error('Error finding spotify song')
                logger.error(response_payload)
                raise Exception(response_payload)
            # Handle the response from the 'spotify_song' Lambda function
            if response['StatusCode'] == 200:
                logger.info('spotify song returned')
                response_body = json.loads(response_payload.get('body'))
                reply = response_body["reply"]
                return reply
            else:
                logger.error(response['StatusCode'])
                raise Exception(
                    f'Tweet was not sent. status code {response["StatusCode"]}.')
        except Exception as e:
            logger.error(
                f'error finding song for date: {date_str}, error: {e}')
            return f'Hello there! It seems you have may have been trying to use my spotify song finding feature, there was an error finding the spotify link for the song on {date_str}. Feel free to try again or try another date.'

    elif 'birthday' in lowercase_message:
        logger.info('birthday reply selected')

        try:
            date_match = re.search(
                r'\b((\d{4}[-/]\d{2}[-/]\d{2})|(\d{2}[-/]\d{2}[-/]\d{4}))\b', message)
            date = dateparser(date_match.group(), fuzzy=True)
            date_str = date.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(
                f'reply not selected the message was: {message}, error:{e}')
            return 'Hello there! It seems you have may have been trying to use my birthday wishing feature, however your date is invalid.'
        try:
            logger.info(f'adding birthday for user: {user} on birthday: {date}')

            dynamodb = boto3.resource('dynamodb') # Instantiate a DynamoDB client
            
            table = dynamodb.Table('Birthdays')
        
            # Insert or update item
            response = table.put_item(
                Item={
                    'username': user,
                    'birthday': date
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'your birthday has been added to the database !'
            else:
                raise Exception(f'error adding birthday to database, response: {response}')
        except Exception as e:
            logger.error(f'error adding birthday to database, {e}')
            return 'your birthday was not added to the datbase due to a technical glitch. please try again.'

    else:
        logger.info(f'reply not selected the message was: {message}')
        return "Hello there! If you send a message containing the word spotify and a date i can send you the number one in that year. Or containing birthday and your D.O.B i'll wish you happy birthday"


def write_spotify_message(data):
    """input is a dictionary from the Spotify class's get_top_song_info method, writes a message to be tweeted"""

    link = data['link']
    song = data['song']
    artist = data['artist']
    date = data['date']
    message = f'The number one song on {date} was {song} by {artist}, listen here:\n{link}'
    return message


lambda_handler(event="", context="")
